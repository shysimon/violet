import pymysql
import traceback
import numpy as np
from app.web.violet_group_function import Group
from flask import jsonify


def get_connection():
    '''
    获取数据库连接
    :return:
    '''
    user = 'violet'
    pwd = 'violetzjhnb'
    host = '45.40.202.216'
    port = 3306
    database = 'violet'
    conn = pymysql.connect(host=host, port=port, user=user, password=pwd, database=database, charset='utf8')

    return conn


def user_to_data(user_id, sim):
    conn = get_connection()
    cursor = conn.cursor()

    sql = 'select user_nickname, password, gender, birthday, motto, thumbs_up_num, user_type, info, email from vuser where user_id = %s'
    cursor.execute(sql, [user_id])
    row = cursor.fetchall()[0]

    data = {'user_id': user_id, 'user_nickname': row[0], 'password': row[1], 'gender': row[2], 'birthday': row[3],
            'motto': row[4], 'thumbs_up_num': row[5], 'user_type': row[6], 'info': row[7], 'email': row[8],
            'similarity': sim}

    return data


def user_to_jsonify(users):
    json_data = {}
    try:
        json_data['code'] = 0
        json_data['data'] = []
        for user in users:
            user_id = user[0]
            if user_id == 0:
                continue
            sim = user[1]
            user_data = user_to_data(user_id, sim)
            json_data['data'].append(user_data)
        return jsonify(json_data)
    except Exception as e:
        print(e.args)
        print(traceback.format_exc())
        json_data['code'] = -1
        json_data.pop('data')
        json_data['errMsg'] = e.args
        return jsonify(json_data)


class GroupRecommendSystem(object):
    @staticmethod
    def load_liked_items():
        '''
        根据数据库查找每一个用户所关注的圈子
        :return:
        '''
        conn = get_connection()
        cursor = conn.cursor()

        sql = 'select distinct user_id from vthumbsup'
        cursor.execute(sql)
        user_ids = cursor.fetchall()

        user_items = {}

        for user_id in user_ids:
            user_id = user_id[0]
            # sql = 'select item_type, item_id from vthumbsup where user_id = %s'
            sql = 'select vgroup.group_id,group_name, create_time,info,thumbs_up_num,follow_num,vgroup.user_id ' \
                  'from user_group, vgroup ' \
                  'where user_group.user_id = 2 ' \
                  'and vgroup.group_id = user_group.group_id'
            cursor.execute(sql, [user_id])
            rows = cursor.fetchall()

            list_items = []
            for row in rows:
                # item = LikedItem(user_id, row[0], row[1])
                item = Group(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
                list_items.append(item)

            user_items[user_id] = list_items

        return user_items

    @staticmethod
    def generate_user_item_matrix(user_items):
        '''
        生成 用户-物品 矩阵
        :param user_items: 字典 user_id与list(items)的键值对
        :return:
        '''
        item_idx = 0
        user_idx = 0
        item_to_idx = {}  # item_id转化为item_idx
        idx_to_item = {}  # item_idx转化为item_id
        user_to_idx = {}  # user_id转化为user_idx
        idx_to_user = {}  # user_idx转化为user_id

        for user_id, list_items in user_items.items():
            user_to_idx[user_id] = user_idx
            idx_to_user[user_idx] = user_id
            user_idx += 1

            for item in list_items:
                composite_key = str(item.item_type) + str(item.item_id)  # 以item_type和item_id组合成一个复合键
                if composite_key not in item_to_idx.keys():  # 判重
                    idx_to_item[item_idx] = composite_key
                    item_to_idx[composite_key] = item_idx
                    item.item_idx = item_idx
                    item.composite_key = composite_key
                    item_idx += 1
                else:
                    item.item_idx = item_to_idx[composite_key]
                    item.composite_key = composite_key

        user_num = len(user_items)
        item_num = len(item_to_idx)
        matrix = np.zeros((user_num, item_num))

        for user_id, list_items in user_items.items():  # 构建 用户-物品 矩阵
            user_idx = user_to_idx[user_id]

            for item in list_items:
                matrix[user_idx][item.item_idx] = 1  # 用户对物品有点赞记录则置为1

        indexes = {
            'user_to_idx': user_to_idx,
            'idx_to_user': idx_to_user,
            'item_to_idx': item_to_idx,
            'idx_to_item': idx_to_item}

        return indexes, matrix

    @staticmethod
    def compute_common_num(row1, row2):
        '''
        计算两个用户点赞记录中共有项目的个数（均为1）
        :param row1: 记录1
        :param row2: 记录2
        :return:
        '''
        length = len(row1)
        cnt = 0

        for i in range(length):
            if row1[i] == 1 and row2[i] == 1:
                cnt += 1

        return cnt

    @staticmethod
    def compute_cosine_similarity(row1, row2):
        '''
        计算两个用户的cosine相似度
        :param row1: 记录1
        :param row2: 记录2
        :return:
        '''
        length = len(row1)
        numer = 0  # 分子
        deno1 = 0  # 分母1
        deno2 = 0  # 分母2

        for i in range(length):
            numer += row1[i] * row2[i]
            deno1 += row1[i] ** 2
            deno2 += row2[i] ** 2

        sim = numer / (deno1 ** 0.5 * deno2 ** 0.5)

        return sim

    @staticmethod
    def cold_start(user_id, matrix, indexes):
        '''
        冷启动 -> 应对用户没有任何点赞记录的情况
        从众原则，某个项目若喜欢人数过半则默认新用户喜欢
        :param user_id:
        :param matrix:
        :param indexes:
        :return:
        '''
        if user_id in indexes['user_to_idx'].keys():  # 判断用户是否有点赞记录 有记录则直接返回
            return indexes, matrix

        user_to_idx = indexes['user_to_idx']
        idx_to_user = indexes['idx_to_user']
        mean_vect = np.mean(matrix, axis=0)
        user_idx = max(idx_to_user.keys()) + 1

        user_to_idx[user_id] = user_idx
        idx_to_user[user_idx] = user_id

        user_vect = (mean_vect >= 0.5) + 0

        matrix = np.insert(matrix, matrix.shape[0], values=user_vect, axis=0)

        return indexes, matrix

    def user_based_recommend(self, user_id, indexes, user_item_matrix, max_recommend_num=10):
        '''
        基于用户的推荐算法
        计算推荐目标用户与其余用户的相似度，根据相似度给出推荐
        :param user_id:
        :param indexes:
        :param user_item_matrix:
        :param max_recommend_num:
        :return:
        '''
        user_to_idx = indexes['user_to_idx']
        idx_to_user = indexes['idx_to_user']
        user_idx = user_to_idx[user_id]
        user_num = user_item_matrix.shape[0]

        # 优化 -> 首先选出与目标用户有交集的用户（实际情况大部分用户无交集）
        target_user = user_item_matrix[user_idx]
        inter_user = np.zeros((user_num, 1))
        inter_user[user_idx] = np.inf

        for i in range(user_num):
            if i == user_idx:
                continue  # 排除自己

            useri = user_item_matrix[i]
            common_num = self.compute_common_num(target_user, useri)
            inter_user[i] = common_num

        # 计算相似度
        user_sims = {}
        for i in range(user_num):
            if inter_user[i] == 0 or inter_user[i] == np.inf:
                continue

            useri_id = idx_to_user[i]
            useri = user_item_matrix[i] # 此处已将用户的索引idx转换为用户的对应id
            sim = self.compute_cosine_similarity(target_user, useri)
            user_sims[useri_id] = sim

        # 按相似度降序排序
        user_sorted = sorted(user_sims.items(), key = lambda x:x[1],reverse = True)
        if len(user_sims) > max_recommend_num: # 超过长度则进行截断
            user_sorted = user_sorted[: max_recommend_num]

        return user_sorted

    def generate_item_sim_matrix(self, user_item_matrix):
        '''
        生成 物品相似度 矩阵
        :param user_item_matrix:
        :return:
        '''
        item_num = user_item_matrix.shape[1]
        item_user_matrix = user_item_matrix.T   # 物品-用户 倒排表
        item_item_matrix = np.zeros((item_num, item_num))
        item_similarity = np.zeros((item_num, item_num))

        # 生成 物品-物品 矩阵
        for i in range(item_num):
            for j in range(i + 1, item_num):
                itemi = item_user_matrix[i]
                itemj = item_user_matrix[j]

                common_num = self.compute_common_num(itemi, itemj)
                item_item_matrix[i][j] = item_item_matrix[j][i] = common_num

        # 计算 物品-物品 相似度
        for i in range(item_num):
            for j in range(i + 1, item_num):
                itemi = item_user_matrix[i]
                itemj = item_user_matrix[j]

                sim = self.compute_cosine_similarity(itemi, itemj)
                item_similarity[i][j] = item_similarity[j][i] = sim

        return item_similarity

    @staticmethod
    def item_based_recommend(user_id, indexes, item_similarity, user_item_matrix, max_recommend_num=10):
        '''
        基于物品的推荐算法
        先计算出物品与物品之间的相似度，
        再根据目标用户以前的行为偏好计算对不同物品的兴趣度，
        最终根据物品兴趣度计算对其他用户的兴趣度
        :param user_id:
        :param indexes:
        :param item_similarity:
        :param user_item_matrix:
        :param max_recommend_num:
        :return:
        '''
        user_to_idx = indexes['user_to_idx']
        idx_to_user = indexes['idx_to_user']
        item_num = item_similarity.shape[0]
        user_idx = user_to_idx[user_id]

        liked_item = np.argwhere(user_item_matrix[user_idx] == 1)
        sim_items = []

        for item in liked_item:
            item_idx = item[0]
            for i in range(item_num):
                if i not in sim_items and item_similarity[item_idx][i] > 0:
                    sim_items.append(i)

        # 用户对item的兴趣
        item_interest = np.zeros((1, item_num))
        for i in range(item_num):
            if i in liked_item:
                item_interest[0][i] = 1
            else:
                for item in liked_item:
                    item_idx = item[0]
                    item_interest[0][i] += item_similarity[item_idx][i]

        # 用户对user的兴趣
        interest_mean = np.sum(user_item_matrix, axis=1)
        interest_mean = interest_mean.reshape(interest_mean.shape[0], 1)
        user_interest = np.dot(user_item_matrix, item_interest.T) / interest_mean

        # 选出兴趣不为0的用户
        user_sims = {}
        for i in range(len(user_interest)):
            if i == user_idx or user_interest[i][0] == 0:
                continue
            useri_id = idx_to_user[i]   # 此处user_idx已变回user_id
            user_sims[useri_id] = user_interest[i][0]

        user_sorted = sorted(user_sims.items(), key = lambda x:x[1],reverse = True)
        if len(user_sorted) > max_recommend_num:
            user_sorted = user_sorted[:, max_recommend_num]

        return user_sorted

    @staticmethod
    def merge_recommend(user_based, item_based, beta=0.6):
        '''
        根据一定权重将 user-based与item-based推荐结果结合
        :param user_based:
        :param item_based:
        :param beta: 权重->item-based结果所占多少
        :return:
        '''
        merged_recommend = {}

        for key, value in user_based:
            merged_recommend[key] = value * (1 - beta)

        for key, value in item_based:
            merged_recommend[key] = merged_recommend.get(key, 0) + value * beta

        merged_sorted = sorted(merged_recommend.items(), key = lambda x:x[1],reverse = True)

        return merged_sorted

    def recommend_group(self, user_id, beta=0.6):
        '''
       对用户进行圈子推荐
        :param user_id: 被推荐用户的id
        :param beta: 权重系数，取值应当在(0, 1] -> 反应user-based推荐与item-based推荐所占比
                    计算方法为β* item-based + (1-β) * user-based
        :return:
        '''
        user_items = self.load_liked_items()
        indexes, user_item_matrix = self.generate_user_item_matrix(user_items)
        indexes, user_item_matrix = self.cold_start(user_id, user_item_matrix, indexes)
        user_based = self.user_based_recommend(user_id=user_id, indexes=indexes,
                                          user_item_matrix=user_item_matrix)
        # print('user-based recommend:\n', user_based)

        item_similarity = self.generate_item_sim_matrix(user_item_matrix)
        item_based = self.item_based_recommend(user_id=user_id, indexes=indexes,
                                          item_similarity=item_similarity,
                                          user_item_matrix=user_item_matrix)
        # print('item_based recommend:\n', item_based)

        merged_recommend = self.merge_recommend(user_based, item_based, beta=beta)
        # print('merged recommend:\n', merged_recommend)

        return merged_recommend