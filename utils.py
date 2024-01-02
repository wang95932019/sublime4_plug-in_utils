import sublime
import sublime_plugin
import json
import random


class FormDataToJsonCommand(sublime_plugin.TextCommand):
	""" 将从浏览器中复制的formdata数据转为json格式 """
	def run(self, edit):
		view = self.view
		# 遍历所有拼接为字符串
		formdata_str:str = "".join([view.substr(region) for region in view.sel()])
		formdata_list = formdata_str.split("&")
		formdata_dict = {}
		for formdata in formdata_list:
			print(formdata.split("="))
			key, value = formdata.split("=")
			formdata_dict[key] = value


		insert_point = view.sel()[0].end()  # 获取第一个选区的结束位置

		line_after_sel = view.line(insert_point).end() + 1  # 获取选区之后一行的位置
		view.insert(edit, line_after_sel, json.dumps(formdata_dict))


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