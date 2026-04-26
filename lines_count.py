# points_list = [[],[],[],[]]
# lines = []
# lines.append([2, points_list[0], points_list[1]])
# def cal_slope(point1, point2):
#     x1 = point1[0]
#     y1 = point1[1]
#     x2 = point2[0]
#     y2 = point2[1]
#     return (y2-y1)/(x1-x2)
# max_p_line = 0
#
# s1 = [0 for _ in range(len(points_list))]
# slope_matrix = [s1[:] for _ in range(len(points_list))]
# for i in range(0,len(slope_matrix)):
#     for j in range(0, len(s1)):
#         slope_matrix[i][j] = cal_slope(points_list[i], points_list[j])
#
# # for point in points_list[2:]:
# for point_ind in range(2, len(points_list)):
#     slope_matches = []
#     point = points_list[point_ind]
#     for line in lines:
#         slope1 = cal_slope(point, lines[1])
#         slope2 = cal_slope(point, lines[2])
#         if slope1 == slope2:
#             slope_matches.append(slope1)
#             line[0] = line[0] + 1
#             if line[0] > max_p_line: max_p_line = line[0]
#     # get all the lines which are not with the same slope with this poit and crate new lines and append to the lines list
#     for slope in slope_matches:
#         slope_pairs = slope_matrix[point]
#         for k in range(len(slope_pairs)):
#             if slope_pairs[k] == slope and k!=point_ind:
#                 lines.append([2, point, points_list[k]])
#
# print(max_p_line)

# class Solution():
#     def getnextL_u(self, x, y, rows):
#         if y == 0 and x + 2 < rows:
#             return x + 2, y
#         elif y == 0 and x == rows - 2:
#             return rows - 1, 1
#         elif y == 0 and x == rows - 1:
#             return rows - 1, 2
#         elif y > 0:
#             return rows - 1, y+2
#
#     def getnextL_d(self, x, y, cols):
#         if x == 0 and y + 2 < cols:
#             return 0, y + 2
#         if x == 0 and y + 2 == cols:
#             return 1, cols - 1
#         if x == 0 and y + 1 == cols:
#             return 2, cols - 1
#         if x > 0:
#             return x + 2, cols - 1
#
#     def findDiagonalOrder(self, mat):
#         """
#         :type mat: List[List[int]]
#         :rtype: List[int]
#         """
#         for i in mat:
#             print(i)
#         i = 0
#         j = 0
#         rows = len(mat)
#         cols = len(mat[0])
#         res = []
#         direction = 1
#
#         strow_d = 0
#         stcol_d = 1
#
#         strow_u = 0
#         stcol_u = 0
#         k = 0
#         total = rows * cols
#
#         if cols == 1:
#             return [i[0] for i in mat]
#         if rows == 1:
#             return mat[0]
#         while k < total:
#             # print(i,j)
#             # print(mat[i][j])
#             res.append(mat[i][j])
#             if direction == 1:
#                 if i - 1 > -1 and j + 1 < cols:
#                     i = i - 1
#                     j = j + 1
#                 else:
#                     direction = 0
#                     # strow_d, stcol_d = self.getnextL_d(strow_d, stcol_d, cols)
#                     i = strow_d
#                     j = stcol_d
#                     strow_u, stcol_u = self.getnextL_u(strow_u, stcol_u, rows)
#             elif direction == 0:
#                 if i + 1 < rows and j - 1 > -1:
#                     i = i + 1
#                     j = j - 1
#                 else:
#                     direction = 1
#                     # strow_u, stcol_u = self.getnextL_u(strow_u, stcol_u, rows)
#                     i = strow_u
#                     j = stcol_u
#                     strow_d, stcol_d = self.getnextL_d(strow_d, stcol_d, cols)
#             k = k + 1
#         print(res)
#         return res
#
# mat = [[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]]
# s = Solution()
# s.findDiagonalOrder(mat)