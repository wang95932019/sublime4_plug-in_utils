import sublime
import sublime_plugin
import json
import random
import urllib.parse


class FormDataToJsonCommand(sublime_plugin.TextCommand):
	""" 将从浏览器中复制的formdata数据转为json格式 """

	def run(self, edit):
		view = self.view
		# 遍历所有拼接为字符串
		formdata_str:str = "".join([view.substr(region) for region in view.sel()])
		formdata_list = formdata_str.split("&")
		formdata_dict = {}
		for formdata in formdata_list:
			try:
				key, value = formdata.split("=")
			except ValueError:
				key = formdata.split("=")
				value = ""

			# unicode解码，如："%E4%BD%A0%E5%A5%BD" 转为 "你好"
			key = urllib.parse.unquote(key)
			value = urllib.parse.unquote(value)
			formdata_dict[key] = value

		# 将 Python 对象转换为 JSON 格式的字符串，并进行格式化
		formatted_json = json.dumps(formdata_dict, indent="\t", ensure_ascii=False)

		# 输出结果
		insert_point = view.sel()[0].end()  # 获取第一个选区的结束位置
		view.insert(edit, insert_point, "\n")       # 先写入换行，否则如果是最后view的最后一行不会有写入
		line_after_sel = view.line(insert_point).end() + 1  # 获取选区之后一行的位置
		view.insert(edit, line_after_sel, formatted_json)


class CreateSocialCreditCommand(sublime_plugin.TextCommand):
	""" 
		生成统一社会信用代码 
		备注：生成虚拟的企业：组织机构代码（八位数字（或大写拉丁字母）本体代码和一位数字（或大写拉丁字母）校验码组成）
			三证合一和一证一码是指工商营业执照，税务登记证，组织机构代码证合并为一张加载统一社会信用代码的营业执照。
			统一社会信用代码：（登记管理部门代码（1位）、机构类别代码（1位）、登记管理机关行政区划码（6位）、主体标识码（组织机构代码）（9位）和校验码（1位）5个部分组成）
	"""
	# 统一社会信用代码最后一位：代码字符集
	check_dict = {
		"0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9,
		"A": 10, "B": 11, "C": 12, "D": 13, "E": 14, "F": 15, "G": 16, "H": 17, "J": 18, "K": 19, "L": 20, "M": 21,
		"N": 22, "P": 23, "Q": 24, "R": 25, "T": 26, "U": 27, "W": 28, "X": 29, "Y": 30
	}
	dict_check = {value: key for key, value in check_dict.items()}


	def run(self, edit):
		# 1. 生成code
		code = self.create_social_credit()
		# 2. 写到光标所在位置
		view = self.view
		insert_points = [region.begin() for region in view.sel()]  # 获取所有选区的开始位置
		for insert_point in reversed(insert_points):
			self.view.insert(edit, insert_point, code)
			break
	 
	 
	# 组织机构代码 9位
	def create_organization(self):
		weight_code = [3,7,9,10,5,8,4,2]      # Wi 代表第i位上的加权因子=pow(3,i-1)%31
		org_code = []                         # 组织机构代码列表
		sum = 0
		for i in range(8):
			org_code.append(self.dict_check[random.randint(0,30)])     # 前八位本体代码：0~9 + A~Z 31个
			sum = sum + self.check_dict[org_code[i]]*weight_code[i]
		C9 = 11-sum % 11                      # 代表校验码：11-MOD（∑Ci(i=1→8)×Wi,11）-->前8位加权后与11取余，然后用11减
		if C9 == 10:
			last_code = 'X'
		elif C9 == 11:
			last_code = '0'
		else:
			last_code = str(C9)
	 
		code = ''.join(org_code) + '-' +last_code     # 组织机构代码
		#print(code)
		return (code)
	 
	 
	# 统一社会信用代码 18位
	def create_social_credit(self):
		manage_code = [9]            # 登记管理部门代码：9-工商
		type_code = [1,2,3,9]        # 9-1-企业，9-2-个体工商户，9-3-农民专业合作社，9-9-其他
		area_code = '100000'         # 登记管理机关行政区划码：100000-国家用
		org_code = self.create_organization().replace('-','')   # 组织机构代码
		sum = 0
		weight_code = [1, 3, 9, 27, 19, 26, 16, 17,20,29,25,13,8,24,10,30,28]     # Wi 代表第i位上的加权因子=pow(3,i-1)%31
		code = str(random.choice(manage_code)) + str(random.choice(type_code)) + area_code + org_code
		for i in range(17):
			sum = sum + self.check_dict[code[i:i+1]]*weight_code[i]
		C18 = self.dict_check[31-sum % 31]
		social_code = code + C18
		return social_code


class GenerateRandomId(sublime_plugin.TextCommand):
	""" 生成身份证号 """

	def run(self, edit):
		# 1. 生成code
		code = self.generate_random_id()
		# 2. 写到光标所在位置
		view = self.view
		insert_points = [region.begin() for region in view.sel()]  # 获取所有选区的开始位置
		for insert_point in reversed(insert_points):
			self.view.insert(edit, insert_point, code)
			break
	
	def generate_random_address_code(self):
		# 生成随机地址码
		address_code = str(random.randint(110000, 659000))
		return address_code

	def generate_random_birth_date_code(self):
		# 生成随机出生日期码
		year = random.randint(1950, 2022)
		month = random.randint(1, 12)
		day = random.randint(1, 28)
		birth_date_code = str(year).zfill(4) + str(month).zfill(2) + str(day).zfill(2)
		return birth_date_code

	def generate_random_sequence_code(self):
		# 生成随机顺序码
		sequence_code = str(random.randint(1, 999)).zfill(3)
		return sequence_code

	def generate_check_code(self, body):
		# 生成校验码
		factors = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
		check_code_dict = {
			0: '1', 1: '0', 2: 'X', 3: '9', 4: '8', 5: '7', 6: '6', 7: '5', 8: '4', 9: '3', 10: '2'
		}
		check_code = 0
		for i in range(len(body)):
			check_code += int(body[i]) * factors[i]
		check_code %= 11
		return check_code_dict[check_code]

	def generate_random_id(self):
		# 生成随机身份证号码
		address_code = self.generate_random_address_code()
		birth_date_code = self.generate_random_birth_date_code()
		sequence_code = self.generate_random_sequence_code()
		body = address_code + birth_date_code + sequence_code
		check_code = self.generate_check_code(body)
		id_number = body + check_code
		return id_number


class GeneratePhoneNumber(sublime_plugin.TextCommand):
	""" 生成手机号 """

	def run(self, edit):
		# 1. 生成code
		code = self.create_a_phone()
		# 2. 写到光标所在位置
		view = self.view
		insert_points = [region.begin() for region in view.sel()]  # 获取所有选区的开始位置
		for insert_point in reversed(insert_points):
			self.view.insert(edit, insert_point, code)
			break

	def create_a_phone(self):
		# 第二位数字
		second = [3, 4, 5, 7, 8][random.randint(0, 4)]

		# 第三位数字
		third = {3: random.randint(0, 9),
				 4: [5, 7, 9][random.randint(0, 2)],
				 5: [i for i in range(10) if i != 4][random.randint(0, 8)],
				 7: [i for i in range(10) if i not in [4, 9]][random.randint(0, 7)],
				 8: random.randint(0, 9), }[second]

		# 最后八位数字
		suffix = random.randint(9999999, 100000000)

		# 拼接手机号
		return "1{}{}{}".format(second, third, suffix)


class GenerateApiStructure(sublime_plugin.TextCommand):
	""" 生成API结构 """

	def run(self, edit):
		view = self.view

		# 获取所选中的第一个区域
		view_first_region = view.substr(view.sel()[0])

		# 处理选中的数据
		view_str_list = view_first_region.split("\n")
		api_name = view_str_list[0]
		parsers_list = list(map(lambda view_str: view_str.strip(), view_str_list[1:]))
		result = self.generate_api_structure(api_name, parsers_list)

		# 获取最后一行的结束位置
		insert_points = [region.end() for region in view.sel()]
		for insert_point in  insert_points:
			last_line_end = view.line(insert_point).end() + 2  # 获取选区之后一行的位置

			# 插入结果到最后一行的下一行
			view.insert(edit, last_line_end, result)
			break



	def generate_api_structure(self, api_name:str, parsers_list:list):
		"""
		生成api结构
		:param api_name: API名称
		:param params_list: 参数列表
		:return:
		"""

		# 模块字典
		module_dict = {
			"views_resource_module": "路由地址模块",
			"parsers_module": "参数模块",
			"resource_module": "资源类模块",
			"res_module": "功能方法模块",
		}

		# 下划线转驼峰命名
		api_name_camel = self.underscoreToCamel(api_name)

		# 前缀字符串
		prefix_str = "================ %s =====================\n"


		# 路由地址
		views_resource_str = prefix_str%module_dict["views_resource_module"] + f"""[{module_dict["resource_module"]}.{api_name_camel}, "/{api_name}", "{api_name}"],"""

		# 参数列表
		parsers_str_list = [f"""{api_name} = reqparse.RequestParser(trim=True)"""]
		for parsers in parsers_list:
			parsers_str_list.append(f"""{api_name}.add_argument("{parsers}", type=str, required=True, default="")""")
		parsers_str = prefix_str%module_dict["parsers_module"] + "\n".join(parsers_str_list)

		# 资源类
		resource_str_list = [
								f"""class {api_name_camel}(Resource):""",
								f"""\tdef post(self):""",
								f"""\t\tconn = get_conn()""",
								f"""\t\tdata = {module_dict["views_resource_module"]}.{api_name}.parse_args()""",
							]
		for parsers in parsers_list:
			resource_str_list.append(f"""\t\t{parsers} = data["{parsers}"]""")
		resource_str_list.append(f"""\t\ttry:""")
		resource_str_list.append(f"""\t\t\tflag, res_data = {module_dict["res_module"]}.{api_name}(""")
		resource_str_list.append(f"""\t\t\t\t{', '.join(parsers_list)}""")
		resource_str_list.append(f"""\t\t\t)""")
		resource_str_list.append(f"""\t\t\tif flag:""")
		resource_str_list.append(f"""\t\t\t\treturn return_0(res_data)""")
		resource_str_list.append(f"""\t\t\telse:""")
		resource_str_list.append(f"""\t\t\t\treturn return_1(res_data)""")
		resource_str_list.append(f"""\t\texcept:""")
		resource_str_list.append(f"""\t\t\tlogger.exception("代码执行异常>>>")""")
		resource_str_list.append(f"""\t\t\treturn return_99("网络错误，请稍后重试")""")

		resource_str = prefix_str%module_dict["resource_module"] + "\n".join(resource_str_list)


		# 功能方法
		res_str_list = [
							f"""def {api_name}({', '.join(parsers_list)}):""",
							f"""\traise NotImplementedError"""
						]

		res_str = prefix_str%module_dict["res_module"] + "\n".join(res_str_list)

		result = views_resource_str + "\n"*2 + parsers_str + "\n"*2 + resource_str + "\n"*2 + res_str
		return result


	def underscoreToCamel(self, underscore_str, is_initial_case:bool=True):
		""" 
		下划线转驼峰命名 
		:param underscore_str: 字符串
		:param is_initial_case: 首字母是否大写
		"""

		# 将下划线分隔的单词转换为列表
		words = underscore_str.split('_')

		# 将每个单词的首字母大写，并拼接成一个字符串
		camel_str = ''.join([word.capitalize() for word in words])

		# 将第一个单词的首字母小写
		if not is_initial_case:
			camel_str = camel_str[0].lower() + camel_str[1:] 

		return camel_str


class ShowPathsCommand(sublime_plugin.WindowCommand):
	""" 输出选中的文件的路径 """
	def run(self, paths):
		print(paths)