
import re

# ------------------------------------------------------------------------- #
#	FUNCTIONS																#
# ------------------------------------------------------------------------- #

# GET THE PAGE CONTENT WITH THE REGULAR EXPRESSION NECESARY

def getPageExpr (page, regularExp):
	f = open (page, 'r')
	text = f.read()
	f.close ()
	# PARSE CONTENT
	return [ [i[0], i[1]] for i in (re.findall (regularExp, text)) ]

# ------------------------------------------------------------------------- #
#	CLASS: [PROTOTYPESHEET]													#
# ------------------------------------------------------------------------- #

class prototypeSheet:

	__regex_prototype = r'@REDefine (@\w+)\s*{\s*(.*)\s*}'
	prototypes = {}

	def __init__(self, page_name):
		# RAWPROTOS -> [[EXP,RAW_DEFINITION],[EXP, RAW_DEFINITION]...
		self.rawProtos = getPageExpr (page_name, self.__regex_prototype)
		# PARSE AND CREATE LIST -> [EXP:[CONT, PROTOTYPE], EXP2:[CONT, PROTOTYPE]...
		for exp_name, exp in self.rawProtos:
			self.prototypes [exp_name] = self.definitionToProto (exp)

	def definitionToProto (self, definition):	# 'a b c d' => (4, '\\1 \\2 \\3 \\4')
		res = []
		cont = 0
		for word in definition.split (' '):
			if word == '': 
				res.append ('')
			else:
				cont += 1
				res.append ('\\'+str(cont))
		return (cont, ' '.join (res))

# x = prototypeSheet ('proto.txt')

# print x.definitionToProto ('@a @b @c')

# ------------------------------------------------------------------------- #
#	CLASS: [BNFSHEET]														#
# ------------------------------------------------------------------------- #

# BNF DEFINITION OF THE LANGUAGE -> REGULAR EXPRESIONS FOR EACH COMPONENT

class BNFSheet:

	__regex_language = r'@Define (@\w+)\s*{\s*(.*)\s*}'
	# REGEX DEFINITION OF SEVERAL SIMPLE STRUCTURES
	bnf_regex = { '@VAR':'\w+', '@ASIG':'\w+', '@OPAND':'&&', '@OPEQ':'==', '@ALL':'.*' }

	def __init__(self, page):
		# BNF LANGUAGE -> [ EXP:['OP1 OP2 OP3'] ...]
		self.rawBNF = getPageExpr (page, self.__regex_language)
		# [ EXP:['OP1','OP2','OP3']... ]
		self.rawBNF = [ [exp_name, exp.split(' ')] for exp_name, exp in self.rawBNF ]
		# GENERATE REGEX FOR ALL ELEMENTS
		for e_name, e_components in self.rawBNF:
			reg = '\s*'.join ([ self.nameToRegex(comp.strip()) for comp in e_components])
			self.bnf_regex[e_name] = reg
		# print self.bnf_regex

	def nameToRegex (self, e_name):	# ['@var','@opeq','@var'] -> Regular expression
		res = e_name
		if '@' in e_name:	# BNF ELEMENT
			if e_name in self.bnf_regex:
				res = self.bnf_regex[e_name].replace ('(','(?:')
			else:
				# ERROR. ELEMENT NOT FOUND YET. TRY TO ADD COMPS BUT IT HAS NOT BEEN GENERATED
				print 'ERROR WITH', e_name

		# SPECIAL CASE '(' ')'
		if res in ['(',')']:
			res = '[' + res + ']'

		# ADD THE GROUP CONTENT
		return '(' + res + ')'

# y = BNFSheet ('sheet.txt')

# ------------------------------------------------------------------------- #
#	[CHANGE FUNCTIONS]														#
# ------------------------------------------------------------------------- #

# GET GROUPS FOR A DETERMINATED REGULAR EXPRESION

def getChangeGroups (text, regex):
	rx = re.compile (regex)
	x = rx.finditer (text)
	# CREATE A LIST WITH THE RESULT
	return [ y.groups() for y in x]

# TO MAKE THE CHANGE, ADD () FOR THE GROUPS AND [] FOR THE '(' ')'

def completeREGEX (exp):
	if exp in ['(',')']:
		exp = '['+exp+']'
	return '('+exp+')'

#
#	TEXT TO MAKE THE CHANGE, THE BNF REGULAR EXPRESION WE ARE LOOKING FOR AND THE PROTOTYPE FOR THE CHANGE
#

def make_change (text, regex, prototype):
	change_groups = getChangeGroups (text, regex)
	for group in change_groups:
		# CREATE ANOTHER REGEX FOR THIS EXPRESSION.
		regex_group = [ completeREGEX (e) for e in group]
		tupleToFind = '\s*'.join (str(a) for a in regex_group)
		# REPLACE IN TEXT
		text = re.sub (tupleToFind, prototype, text, 1)	# JUST ONE CHANGE
	return text

# ------------------------------------------------------------------------- #
#	[IMPLEMENTATION]														#
# ------------------------------------------------------------------------- #

text = 'if (x  ==y)             { \nif        (p   ==o)   {\nwhile    (x == y) {\n'

p_sheet = prototypeSheet ('proto.txt')
bnf_sheet = BNFSheet ('sheet.txt')

for key, (elem, proto) in p_sheet.prototypes.iteritems():
	if key in bnf_sheet.bnf_regex:
		text = make_change (text, bnf_sheet.bnf_regex [key], proto)

print text
