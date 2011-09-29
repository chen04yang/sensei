#!/usr/bin/env python
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Python client library for Sensei
"""

import urllib
import urllib2
import json
import sys
import logging

logger = logging.getLogger("sensei_client")

# TODO:
#
# 1. Initializing runtime facet parameters
# 2. Term vector

#
# REST API parameter constants
#
PARAM_OFFSET = "start"
PARAM_COUNT = "rows"
PARAM_QUERY = "q"
PARAM_QUERY_PARAM = "qparam"
PARAM_SORT = "sort"
PARAM_SORT_ASC = "asc"
PARAM_SORT_DESC = "desc"
PARAM_SORT_SCORE = "relevance"
PARAM_SORT_SCORE_REVERSE = "relrev"
PARAM_SORT_DOC = "doc"
PARAM_SORT_DOC_REVERSE = "docrev"
PARAM_FETCH_STORED = "fetchstored"
PARAM_SHOW_EXPLAIN = "showexplain"
PARAM_ROUTE_PARAM = "routeparam"
PARAM_GROUP_BY = "groupby"
PARAM_MAX_PER_GROUP = "maxpergroup"
PARAM_SELECT = "select"
PARAM_SELECT_VAL = "val"
PARAM_SELECT_NOT = "not"
PARAM_SELECT_OP = "op"
PARAM_SELECT_OP_AND = "and"
PARAM_SELECT_OP_OR = "or"
PARAM_SELECT_PROP = "prop"
PARAM_FACET = "facet"
PARAM_DYNAMIC_INIT = "dyn"
PARAM_PARTITIONS = "partitions"

PARAM_FACET_EXPAND = "expand"
PARAM_FACET_MAX = "max"
PARAM_FACET_MINHIT = "minhit"
PARAM_FACET_ORDER = "order"
PARAM_FACET_ORDER_HITS = "hits"
PARAM_FACET_ORDER_VAL = "val"

PARAM_DYNAMIC_TYPE = "type"
PARAM_DYNAMIC_TYPE_STRING = "string"
PARAM_DYNAMIC_TYPE_BYTEARRAY = "bytearray"
PARAM_DYNAMIC_TYPE_BOOL = "boolean"
PARAM_DYNAMIC_TYPE_INT = "int"
PARAM_DYNAMIC_TYPE_LONG = "long"
PARAM_DYNAMIC_TYPE_DOUBLE = "double"
PARAM_DYNAMIC_VAL = "vals"

PARAM_RESULT_PARSEDQUERY = "parsedquery"
PARAM_RESULT_HIT_STORED_FIELDS = "stored"
PARAM_RESULT_HIT_STORED_FIELDS_NAME = "name"
PARAM_RESULT_HIT_STORED_FIELDS_VALUE = "val"
PARAM_RESULT_HIT_EXPLANATION = "explanation"
PARAM_RESULT_FACETS = "facets"

PARAM_RESULT_TID = "tid"
PARAM_RESULT_TOTALDOCS = "totaldocs"
PARAM_RESULT_NUMHITS = "numhits"
PARAM_RESULT_HITS = "hits"
PARAM_RESULT_HIT_UID = "uid"
PARAM_RESULT_HIT_DOCID = "docid"
PARAM_RESULT_HIT_SCORE = "score"
PARAM_RESULT_HIT_SRC_DATA = "srcdata"
PARAM_RESULT_TIME = "time"

PARAM_SYSINFO_NUMDOCS = "numdocs"
PARAM_SYSINFO_LASTMODIFIED = "lastmodified"
PARAM_SYSINFO_VERSION = "version"
PARAM_SYSINFO_FACETS = "facets"
PARAM_SYSINFO_FACETS_NAME = "name"
PARAM_SYSINFO_FACETS_RUNTIME = "runtime"
PARAM_SYSINFO_FACETS_PROPS = "props"
PARAM_SYSINFO_CLUSTERINFO = "clusterinfo"
PARAM_SYSINFO_CLUSTERINFO_ID = "id"
PARAM_SYSINFO_CLUSTERINFO_PARTITIONS = "partitions"
PARAM_SYSINFO_CLUSTERINFO_NODELINK = "nodelink"
PARAM_SYSINFO_CLUSTERINFO_ADMINLINK = "adminlink"

PARAM_RESULT_HITS_EXPL_VALUE = "value"
PARAM_RESULT_HITS_EXPL_DESC = "description"
PARAM_RESULT_HITS_EXPL_DETAILS = "details"

PARAM_RESULT_FACET_INFO_VALUE = "value"
PARAM_RESULT_FACET_INFO_COUNT = "count"
PARAM_RESULT_FACET_INFO_SELECTED = "selected"

# Group by related column names
GROUP_VALUE = "groupvalue"
GROUP_HITS = "grouphits"

#
# Definition of the SQL statement grammar
#

from pyparsing import Literal, CaselessLiteral, Word, Upcase, delimitedList, Optional, \
    Combine, Group, alphas, nums, alphanums, ParseException, Forward, oneOf, quotedString, \
    ZeroOrMore, restOfLine, Keyword, OnlyOnce

"""

BNF Grammar for BQL
===================

<select_stmt> ::=  SELECT <select_list> <from_clause> <where_clause> <given_clause> <additional_specs> [';']

<select_list> ::=  '*' | <column_list>
<column_list> ::=  <column_name> ( ',' <column_name> )*

<from_clause> ::=  FROM <index_name>

<where_clause> ::=  WHERE <search_condition>
<search_condition> ::=  <predicates>

<predicates> ::=  <predicate> ( AND <predicate> )*
<predicate> ::=  <query_predicate> | <column_predicate>

<query_predicate> ::=  QUERY IS <quoted_string>
<column_predicate> ::=  <column_name> <column_condition> [<prop_clause>]

<column_condition> ::=  <column_positive_operator> <value_list> [<except_clause>]
                        | <column_negative_operator> <value_list>
<column_positive_operator> ::=  IN | CONTAINS ALL
<column_negative_operator> ::=  NOT IN
<value_list> ::= '(' <quoted_string> ( ',' <quoted_string> )* ')'

<except_clause> ::=  EXCEPT <value_list>

<prop_clause> ::=  WITH <prop_list>

<prop_list> ::=  '(' <key_value_pair> ( ',' <key_value_pair> )* ')'
<key_value_pair> ::=  <quoted_string> ':' <quoted_string>

<given_clause> ::= GIVEN FACET PARAM <facet_param_list>
<facet_param_list> ::= <facet_param> ( ',' <facet_param> )*
<facet_param> ::=  '(' <facet_name> <facet_param_name> <facet_param_type> <facet_param_value> ')'
<facet_param_name> ::= <quoted_string>
<facet_param_type> ::= BOOLEAN | INT | LONG | STRING | BYTEARRAY | DOUBLE
<facet_param_value> ::= <quoted_string>

<additional_specs> ::=  ( <order_by_clause>
                          | <group_by_clause>
                          | <limit_clause>
                          | <browse_by_clause> )*

<order_by_clause> ::=  ORDER BY <sort_specs>
<sort_specs> ::=  <sort_spec> ( ',', <sort_spec> )*
<sort_spec> ::=  <column_name> [<ordering_spec>]
<ordering_spec> ::=  ASC | DESC

<group_by_clause> ::=  GROUP BY <group_spec>
<group_spec> ::=  <facet_name> [TOP <max_per_group>]

<limit_clause> ::=  LIMIT [<offset> ','] <count>
<offset> ::=  ( <digit> )+
<count> ::=  ( <digit> )+

<browse_by_clause> ::=  BROWSE BY <facet_spec_list>
<facet_spec_list> ::=  '(' <facet_specs> ')'
<facet_specs> ::=  <facet_spec> ( ',' <facet_spec> )*
<facet_spec> ::=  <facet_name> ':' <facet_expression>
<facet_expression> ::=  '(' <expand_flag> <count> <count> <facet_ordering> ')'
<expand_flag> ::= TRUE | FALSE
<facet_ordering> ::=  HITS | VALUE

<quoted_string> ::=  '"' ( <char> )* '"'

"""


# A dummy parse action used to make sure that some clause appears
# only once.

def dummy_action(s, loc, tok):
  pass

limit_once = OnlyOnce(dummy_action)
order_by_once = OnlyOnce(dummy_action)
group_by_once = OnlyOnce(dummy_action)
browse_by_once = OnlyOnce(dummy_action)

def reset_all():
  limit_once.reset()
  order_by_once.reset()
  group_by_once.reset()
  browse_by_once.reset()

# SQL tokens

andToken        = Keyword("and", caseless=True)
ascToken        = Keyword("asc", caseless=True)
booleanToken    = Keyword("boolean", caseless=True)
browseByToken   = Keyword("browse by", caseless=True)
byteToken       = Keyword("bytearray", caseless=True)
containsToken   = Keyword("contains all", caseless=True)
descToken       = Keyword("desc", caseless=True)
doubleToken     = Keyword("double", caseless=True)
exceptToken     = Keyword("except", caseless=True)
facetParamToken = Keyword("facet param", caseless=True)
falseToken      = Keyword("false", caseless=True)
fromToken       = Keyword("from", caseless=True)
groupByToken    = Keyword("group by", caseless=True)
givenToken      = Keyword("given", caseless=True)
hitsToken       = Keyword("hits", caseless=True)
inToken         = Keyword("in", caseless=True)
intToken        = Keyword("int", caseless=True)
isToken         = Keyword("is", caseless=True)
limitToken      = Keyword("limit", caseless=True)
longToken       = Keyword("long", caseless=True)
notInToken      = Keyword("not in", caseless=True)
orderbyToken    = Keyword("order by", caseless=True)
withToken       = Keyword("with", caseless=True)
queryToken      = Keyword("query", caseless=True)
selectToken     = Keyword("select", caseless=True)
stringToken     = Keyword("string", caseless=True)
topToken        = Keyword("top", caseless=True)
trueToken       = Keyword("true", caseless=True)
valueToken      = Keyword("value", caseless=True)
whereToken      = Keyword("where", caseless=True)

selectStmt      = Forward()

ident           = Word(alphas, alphanums + "_$")
columnName      = Word(alphas, alphanums + "_-")
facetName       = Word(alphas, alphanums + "_-")
columnNameList  = Group(delimitedList(columnName))

whereExpression = Forward()

intNum = Word(nums)

propPair = (quotedString + ":" + quotedString)
quotedStringList = "(" + delimitedList(quotedString) + ")"

columnPositiveOperator = inToken | containsToken
columnNegativeOperator = notInToken
columnCondition = ((columnPositiveOperator +
                    quotedStringList.setResultsName("value_list") +
                    Optional(exceptToken + quotedStringList.setResultsName("except_values"))) |
                   (columnNegativeOperator + quotedStringList.setResultsName("not_in_list")))

whereCondition = Group((columnName + columnCondition +
                        Optional(withToken + "(" + delimitedList(propPair).setResultsName("prop_list") + ")")
                        ) |
                       (queryToken + isToken + quotedString)
                       )
whereExpression << (whereCondition.setResultsName("condition", listAllMatches=True) +
                    ZeroOrMore(andToken + whereExpression))

paramType = booleanToken | intToken | longToken | stringToken | byteToken | doubleToken
facetParam = ("(" + facetName + "," + quotedString + "," +
              paramType + "," + quotedString + ")").setResultsName("facet_param", listAllMatches=True)
givenClause = (givenToken + facetParamToken + delimitedList(facetParam))

orderseq    = ascToken | descToken

orderByExpression = Forward()
orderBySpec = Group(columnName + Optional(orderseq))
orderByExpression << (orderBySpec.setResultsName("orderby_spec", listAllMatches=True) +
                      ZeroOrMore("," + orderByExpression))
orderByClause = (orderbyToken + orderByExpression).setResultsName("orderby").setParseAction(order_by_once)

limitClause = (limitToken
               + Group(Optional(intNum + ",") + intNum)).setResultsName("limit").setParseAction(limit_once)

trueOrFalse = trueToken | falseToken
facetOrderBy = hitsToken | valueToken
facetSpec = Group(columnName + ":" + "(" + trueOrFalse + "," + intNum  + "," + intNum + "," + facetOrderBy + ")")
browseByClause = (browseByToken +
                  "(" + delimitedList(facetSpec).setResultsName("facet_specs") + ")").setParseAction(browse_by_once)

groupByClause = (groupByToken +
                 columnName.setResultsName("groupby") +
                 Optional(topToken + intNum.setResultsName("max_per_group"))).setParseAction(group_by_once)

selectStmt << (selectToken + 
               ('*' | columnNameList).setResultsName("columns") + 
               fromToken + 
               ident.setResultsName("index") + 
               Optional(whereToken + whereExpression.setResultsName("where")) +
               Optional(givenClause.setResultsName("given")) +
               ZeroOrMore(orderByClause |
                          limitClause |
                          browseByClause |
                          groupByClause
                          ) +
               Optional(";")
               )

simpleSQL = selectStmt

# Define comment format, and ignore them
sqlComment = "--" + restOfLine
simpleSQL.ignore(sqlComment)


class SQLRequest:
  """A Sensei request with a SQL SELECT-like statement."""

  def __init__(self, sql_stmt):
    try:
      self.tokens = simpleSQL.parseString(sql_stmt, parseAll=True)
    except ParseException as err:
      raise err
    finally:
      reset_all()
    self.query = ""
    self.selections = []
    self.sorts = None
    self.columns = [str(col) for col in self.tokens.columns]
    self.facet_init_param_map = None

    where = self.tokens.where
    if where:
      for cond in where.condition:
        if cond[0] == "query" and cond[1] == "is":
          self.query = cond[2][1:-1]
        else:
          if cond[1] == "in" or cond[1] == "not in":
            operation = PARAM_SELECT_OP_OR
          else:
            operation = PARAM_SELECT_OP_AND
          select = SenseiSelection(cond[0], operation)
          if cond[1] != "not in":
            for val in cond.value_list[1:-1]:
              select.addSelection(val[1:-1])
            for val in cond.except_values[1:-1]:
              select.addSelection(val[1:-1], True)
          else:
            for val in cond.not_in_list[1:-1]:
              select.addSelection(val[1:-1], True)
          for i in xrange(0, len(cond.prop_list), 3):
            select.addProperty(cond.prop_list[i][1:-1], cond.prop_list[i+2][1:-1])
          self.selections.append(select)

  def get_offset(self):
    """Get the offset."""

    limit = self.tokens.limit
    if limit:
      if len(limit[1]) == 3:
        return int(limit[1][0])
      else:
        return None
    else:
      return None

  def get_count(self):
    """Get the count (default 10)."""

    limit = self.tokens.limit
    if limit:
      if len(limit[1]) == 3:
        return int(limit[1][2])
      else:
        return int(limit[1][0])
    else:
      return None

  def get_index(self):
    """Get the index (i.e. table) name."""

    return self.tokens.index

  def get_columns(self):
    """Get the list of selected columns."""

    return self.columns

  def get_query(self):
    """Get the query string."""

    return self.query

  def get_sorts(self):
    """Get the SenseiSort array base on ORDER BY."""

    if self.sorts:
      return self.sorts

    self.sorts = []
    orderby = self.tokens.orderby
    if orderby:
      orderby_spec = orderby.orderby_spec
      for spec in orderby_spec:
        if len(spec) == 1:
          self.sorts.append(SenseiSort(spec[0]))
        else:
          self.sorts.append(SenseiSort(spec[0], spec[1] == "desc" and True or False))
    return self.sorts

  def get_selections(self):
    """Get all the selections from in statement."""

    return self.selections

  def get_facets(self):
    """Get facet specs."""

    facet_specs = self.tokens.facet_specs
    if not facet_specs:
      return {}
    facets = {}
    for spec in facet_specs:
      facet = SenseiFacet(spec[3] == "true" and True or False,
                          int(spec[5]),
                          int(spec[7]),
                          spec[9] == "hits" and PARAM_FACET_ORDER_HITS or PARAM_FACET_ORDER_VAL)
      facets[spec[0]] = facet
    return facets

  def get_groupby(self):
    """Get group by facet name."""

    if self.tokens.groupby:
      return str(self.tokens.groupby)
    else:
      return None

  def get_max_per_group(self):
    """Get max_per_group value."""

    if self.tokens.max_per_group:
      return int(self.tokens.max_per_group)
    else:
      return None

  def get_facet_init_param_map(self):
    if self.facet_init_param_map:
      return self.facet_init_param_map

    self.facet_init_param_map = {}
    given = self.tokens.given
    if given:
      for param in given.facet_param:
        facet = param[1]
        name = param[3][1:-1]
        param_type = param[5]
        value = param[7][1:-1]
        init_param = SenseiFacetInitParams()

        if param_type == "boolean":
          init_param.put_bool_param(name, value)
        elif param_type == "int":
          init_param.put_int_param(name, value)
        elif param_type == "long":
          init_param.put_long_param(name, value)
        elif param_type == "string":
          init_param.put_string_param(name, value)
        elif param_type == "bytearray":
          init_param.put_byte_param(name, value)
        elif param_type == "double":
          init_param.put_double_param(name, value)

        self.facet_init_param_map[facet] = init_param

    return self.facet_init_param_map


def test(str):
  # print str,"->"
  try:
    tokens = simpleSQL.parseString(str)
    print "tokens = ",        tokens
    print "tokens.columns =", tokens.columns
    print "tokens.index =",  tokens.index
    print "tokens.where =", tokens.where

    print "tokens.where = ", tokens.where
    if tokens.where:
      print "tokens.where.condition = ", tokens.where.condition
      for cond in tokens.where.condition:
        print "cond.value_list = ", cond.value_list
        print "cond.except_values = ", cond.except_values
        print "cond.prop_list = ", cond.prop_list
    print "tokens.orderby = ", tokens.orderby
    if tokens.orderby:
      print "tokens.orderby.orderby_spec = ", tokens.orderby.orderby_spec
    print "tokens.limit = ", tokens.limit
    print "tokens.facet_specs = ", tokens.facet_specs
    print "tokens.groupby = ", tokens.groupby
    print "tokens.max_per_group = ", tokens.max_per_group
    print "tokens.given = ", tokens.given
    if tokens.given:
      print "tokens.given.facet_param = ", tokens.given.facet_param
  except ParseException as err:
    print " "*err.loc + "^\n" + err.msg
  finally:
    reset_all()
  print


class SenseiClientError(Exception):
  """Exception raised for all errors related to Sensei client."""

  def __init__(self, value):
    self.value = value

  def __str__(self):
    return repr(self.value)


class SenseiFacet:
  def __init__(self,expand=False,minHits=1,maxCounts=10,orderBy=PARAM_RESULT_HITS):
    self.expand = expand
    self.minHits = minHits
    self.maxCounts = maxCounts
    self.orderBy = orderBy


class SenseiSelection:
  def __init__(self, field, operation=PARAM_SELECT_OP_OR):
    self.field = field
    self.operation = operation
    self.values = []
    self.excludes = []
    self.properties = {}

  def __str__(self):
    return ("Selection:%s:%s:%s:%s" %
            (self.field, self.operation,
             ','.join(self.values), ','.join(self.excludes)))
    
  def addSelection(self, value, isNot=False):
    if isNot:
      self.excludes.append(value)
    else:
      self.values.append(value)
  
  def removeSelection(self, value, isNot=False):
    if isNot:
      self.excludes.remove(value)
    else:
      self.values.remove(value)
  
  def addProperty(self, name, value):
    self.properties[name] = value
  
  def removeProperty(self, name):
    del self.properties[name]

  def getSelectNotParam(self):
    return "%s.%s.%s" % (PARAM_SELECT, self.field, PARAM_SELECT_NOT)

  def getSelectNotParamValues(self):
    return ",".join(self.excludes)

  def getSelectOpParam(self):
    return "%s.%s.%s" % (PARAM_SELECT, self.field, PARAM_SELECT_OP)

  def getSelectValParam(self):
    return "%s.%s.%s" % (PARAM_SELECT, self.field, PARAM_SELECT_VAL)

  def getSelectValParamValues(self):
    return ",".join(self.values)

  def getSelectPropParam(self):
    return "%s.%s.%s" % (PARAM_SELECT, self.field, PARAM_SELECT_PROP)

  def getSelectPropParamValues(self):
    return ",".join(key + ":" + self.properties.get(key)
        for key in self.properties.keys())
  

class SenseiSort:
  def __init__(self, field, reverse=False):
    self.field = field
    if not (field == PARAM_SORT_SCORE or
            field == PARAM_SORT_SCORE_REVERSE or
            field == PARAM_SORT_DOC or
            field == PARAM_SORT_DOC_REVERSE):
      if reverse:
        self.dir = PARAM_SORT_DESC
      else:
        self.dir = PARAM_SORT_ASC

  def __str__(self):
    return "%s:%s" % (self.field, self.dir)

  def buildSortField(self):
    if self.dir == "":
      return self.field
    else:
      return self.field + ":" + self.dir


class SenseiFacetInitParams:
  """FacetHandler initialization parameters."""

  def __init__(self):
    self.bool_map = {}
    self.int_map = {}
    self.long_map = {}
    self.string_map = {}
    self.byte_map = {}
    self.double_map = {}

  # Getters for param names for different types
  def get_bool_param_names(self):
    return self.bool_map.keys()

  def get_int_param_names(self):
    return self.int_map.keys()

  def get_long_param_names(self):
    return self.long_map.keys()

  def get_string_param_names(self):
    return self.string_map.keys()

  def get_byte_param_names(self):
    return self.byte_map.keys()
  
  def get_double_param_names(self):
    return self.double_map.keys()

  # Add param name, values
  def put_bool_param(self, key, value):
    if isinstance(value, list):
      self.bool_map[key] = value
    else:
      self.bool_map[key] = [value]

  def put_int_param(self, key, value):
    if isinstance(value, list):
      self.int_map[key] = value
    else:
      self.int_map[key] = [value]

  def put_long_param(self, key, value):
    if isinstance(value, list):
      self.long_map[key] = value
    else:
      self.long_map[key] = [value]

  def put_string_param(self, key, value):
    if isinstance(value, list):
      self.string_map[key] = value
    else:
      self.string_map[key] = [value]

  def put_byte_param(self, key, value):
    if isinstance(value, list):
      self.byte_map[key] = value
    else:
      self.byte_map[key] = [value]

  def put_double_param(self, key, value):
    if isinstance(value, list):
      self.double_map[key] = value
    else:
      self.double_map[key] = [value]

  # Getters of param value(s) based on param names
  def get_bool_param(self, key):
    return self.bool_map.get(key)

  def get_int_param(self, key):
    return self.int_map.get(key)

  def get_long_param(self, key):
    return self.long_map.get(key)

  def get_string_param(self, key):
    return self.string_map.get(key)

  def get_byte_param(self, key):
    return self.byte_map.get(key)

  def get_double_param(self, key):
    return self.double_map.get(key)


class SenseiRequest:

  def __init__(self, sql_stmt=None, offset=0, count=10, max_per_group=10):
    self.qParam = {}
    self.explain = False
    self.route_param = None
    self.sql_stmt = sql_stmt

    if sql_stmt:
      sql_req = SQLRequest(sql_stmt)
      self.query = sql_req.get_query()
      self.offset = sql_req.get_offset() or offset
      self.count = sql_req.get_count() or count
      self.columns = sql_req.get_columns()
      self.sorts = sql_req.get_sorts()
      self.selections = sql_req.get_selections()
      self.facets = sql_req.get_facets()
      # PARAM_RESULT_HIT_STORED_FIELDS is a reserved column name.  If this
      # column is selected, turn on fetch_stored flag automatically.
      if PARAM_RESULT_HIT_STORED_FIELDS in self.columns:
        self.fetch_stored = True
      else:
        self.fetch_stored = False
      self.groupby = sql_req.get_groupby()
      self.max_per_group = sql_req.get_max_per_group() or max_per_group
      self.facet_init_param_map = sql_req.get_facet_init_param_map()
    else:
      self.query = None
      self.offset = offset
      self.count = count
      self.columns = []
      self.sorts = None
      self.selections = []
      self.facets = {}
      self.fetch_stored = False
      self.groupby = None
      self.max_per_group = max_per_group
      self.facet_init_param_map = {}

  def get_columns(self):
    return self.columns

  
# XXX Do we really need this class?
class SenseiHit:
  def __init__(self):
    self.docid = None
    self.uid = None
    self.srcData = {}
    self.score = None
    self.explanation = None
    self.stored = None
  
  def load(self, jsonHit):
    self.docid = jsonHit.get(PARAM_RESULT_HIT_DOCID)
    self.uid = jsonHit.get(PARAM_RESULT_HIT_UID)
    self.score = jsonHit.get(PARAM_RESULT_HIT_SCORE)
    srcStr = jsonHit.get(PARAM_RESULT_HIT_SRC_DATA)
    self.explanation = jsonHit.get(PARAM_RESULT_HIT_EXPLANATION)
    self.stored = jsonHit.get(PARAM_RESULT_HIT_STORED_FIELDS)
    if srcStr:
      self.srcData = json.loads(srcStr)
    else:
      self.srcData = None
  

class SenseiResultFacet:
  value = None
  count = None
  selected = None
  
  def load(self,json):
    self.value=json.get(PARAM_RESULT_FACET_INFO_VALUE)
    self.count=json.get(PARAM_RESULT_FACET_INFO_COUNT)
    self.selected=json.get(PARAM_RESULT_FACET_INFO_SELECTED,False)

  
class SenseiResult:
  """Sensei search results for a query."""

  def __init__(self, jsonData):
    logger.debug("jsonData = %s" % jsonData)
    self.jsonMap = jsonData
    self.parsedQuery = jsonData.get(PARAM_RESULT_PARSEDQUERY)
    self.totalDocs = jsonData.get(PARAM_RESULT_TOTALDOCS,0)
    self.time = jsonData.get(PARAM_RESULT_TIME,0)
    self.numHits = jsonData.get(PARAM_RESULT_NUMHITS,0)
    self.hits = jsonData.get(PARAM_RESULT_HITS)
    map = jsonData.get(PARAM_RESULT_FACETS)
    self.facetMap = {}
    if map:
      for k,v in map.items():
        facetList = []
        for facet in v:
          facetObj = SenseiResultFacet()
          facetObj.load(facet)
          facetList.append(facetObj)
        self.facetMap[k]=facetList

  def display(self, columns=['*'], max_col_disp_len=40):
    """Print the results in SQL SELECT result format."""

    keys = []
    max_lens = None
    has_group_hits = False

    def get_max_lens(columns):
      max_lens = {}
      has_group_hits = False
      for col in columns:
        max_lens[col] = len(col)
      for hit in self.hits:
        group_hits = [hit]
        if hit.has_key(GROUP_HITS):
          group_hits = hit.get(GROUP_HITS)
          has_group_hits = True
        for group_hit in group_hits:
          for col in columns:
            if group_hit.has_key(col):
              v = group_hit.get(col)
            else:
              v = '<Not Found>'
            if isinstance(v, list):
              v = ','.join([str(item) for item in v])
            elif isinstance(v, (int, long, float)):
              v = str(v)
            value_len = len(v)
            if value_len > max_lens[col]:
              max_lens[col] = min(value_len, self.max_col_disp_len)
      return max_lens, has_group_hits

    def print_line(char='-', sep_char='+'):
      sys.stdout.write(sep_char)
      for key in keys:
        sys.stdout.write(char * (max_lens[key] + 2) + sep_char)
      sys.stdout.write('\n')

    def print_header():
      if has_group_hits:
        print_line('=', '=')
      else:
        print_line('-', '+')
      sys.stdout.write('|')
      for key in keys:
        sys.stdout.write(' %s%s |' % (key, ' ' * (max_lens[key] - len(key))))
      sys.stdout.write('\n')
      if has_group_hits:
        print_line('=', '=')
      else:
        print_line('-', '+')

    def print_footer():
      if has_group_hits:
        print_line('=', '=')
      else:
        print_line('-', '+')
      sys.stdout.write('%s %s%s in set, %s hit%s, %s total doc%s\n' %
                       (len(self.hits),
                        has_group_hits and 'group' or 'row',
                        len(self.hits) > 1 and 's' or '',
                        self.numHits,
                        self.numHits > 1 and 's' or '',
                        self.totalDocs,
                        self.totalDocs > 1 and 's' or ''))

    self.max_col_disp_len = max_col_disp_len
    if not self.hits:
      print "No hit is found."
      return
    elif not columns:
      print "No column is selected."
      return

    if len(columns) == 1 and columns[0] == '*':
      keys = self.hits[0].keys()
      if GROUP_HITS in keys:
        keys.remove(GROUP_HITS)
      if GROUP_VALUE in keys:
        keys.remove(GROUP_VALUE)
      if PARAM_RESULT_HIT_SRC_DATA in keys:
        keys.remove(PARAM_RESULT_HIT_SRC_DATA)
    else:
      keys = columns

    max_lens, has_group_hits = get_max_lens(keys)

    print_header()

    # Print the results
    for hit in self.hits:
      group_hits = [hit]
      if hit.has_key(GROUP_HITS):
        group_hits = hit.get(GROUP_HITS)
      for group_hit in group_hits:
        sys.stdout.write('|')
        for key in keys:
          if group_hit.has_key(key):
            v = group_hit.get(key)
          else:
            v = '<Not Found>'
          if isinstance(v, list):
            v = ','.join([str(item) for item in v])
          elif isinstance(v, (int, float, long)):
            v = str(v)
          if len(v) > self.max_col_disp_len:
            v = v[:self.max_col_disp_len]
          sys.stdout.write(' %s%s |' % (v, ' ' * (max_lens[key] - len(v))))
        sys.stdout.write('\n')
      if has_group_hits:
        print_line()

    # Print the result footer
    print_footer()

    # Print facet information
    for facet, values in self.jsonMap.get(PARAM_RESULT_FACETS).iteritems():
      max_val_len = len(facet)
      max_count_len = 1
      for val in values:
        max_val_len = max(max_val_len, min(self.max_col_disp_len, len(val.get('value'))))
        max_count_len = max(max_count_len, len(str(val.get('count'))))
      total_len = max_val_len + 2 + max_count_len + 3

      sys.stdout.write('+' + '-' * total_len + '+\n')
      sys.stdout.write('| ' + facet + ' ' * (total_len - len(facet) - 1) + '|\n')
      sys.stdout.write('+' + '-' * total_len + '+\n')

      for val in values:
        sys.stdout.write('| %s%s (%s)%s |\n' %
                         (val.get('value'),
                          ' ' * (max_val_len - len(val.get('value'))),
                          val.get('count'),
                          ' ' * (max_count_len - len(str(val.get('count'))))))
      sys.stdout.write('+' + '-' * total_len + '+\n')
  
class SenseiClient:
  """Sensei client class."""

  def __init__(self,host='localhost',port=8080,path='sensei'):
    self.host = host
    self.port = port
    self.path = path
    self.url = 'http://%s:%d/%s' % (self.host,self.port,self.path)
    self.opener = urllib2.build_opener()
    self.opener.addheaders = [('User-agent', 'Python-urllib/2.5')]
    self.opener.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_7) AppleWebKit/534.30 (KHTML, like Gecko) Chrome/12.0.742.91 Safari/534.30')]
    
  @staticmethod
  def buildUrlString(req):
    paramMap = {}
    paramMap[PARAM_OFFSET] = req.offset
    paramMap[PARAM_COUNT] = req.count
    if req.query:
      paramMap[PARAM_QUERY]=req.query
    if req.explain:
      paramMap[PARAM_SHOW_EXPLAIN] = "true"
    if req.fetch_stored:
      paramMap[PARAM_FETCH_STORED] = "true"
    if req.route_param:
      paramMap[PARAM_ROUTE_PARAM] = req.route_param

    # paramMap["offset"] = req.offset
    # paramMap["count"] = req.count

    if req.sorts:
      paramMap[PARAM_SORT] = ",".join(sort.buildSortField() for sort in req.sorts)

    if req.qParam.get("query"):
      paramMap[PARAM_QUERY] = req.qParam.get("query")
    paramMap[PARAM_QUERY_PARAM] = ",".join(param + ":" + req.qParam.get(param)
                                           for param in req.qParam.keys() if param != "query")

    for selection in req.selections:
      paramMap[selection.getSelectNotParam()] = selection.getSelectNotParamValues()
      paramMap[selection.getSelectOpParam()] = selection.operation
      paramMap[selection.getSelectValParam()] = selection.getSelectValParamValues()
      if selection.properties:
        paramMap[selection.getSelectPropParam()] = selection.getSelectPropParamValues()

    for facet_name, facet_spec in req.facets.iteritems():
      paramMap["%s.%s.%s" % (PARAM_FACET, facet_name, PARAM_FACET_MAX)] = facet_spec.maxCounts
      paramMap["%s.%s.%s" % (PARAM_FACET, facet_name, PARAM_FACET_ORDER)] = facet_spec.orderBy
      paramMap["%s.%s.%s" % (PARAM_FACET, facet_name, PARAM_FACET_EXPAND)] = facet_spec.expand
      paramMap["%s.%s.%s" % (PARAM_FACET, facet_name, PARAM_FACET_MINHIT)] = facet_spec.minHits

    for facet_name, initParams in req.facet_init_param_map.iteritems():
      for name, vals in initParams.bool_map.iteritems():
        paramMap["%s.%s.%s.%s" %
                 (PARAM_DYNAMIC_INIT, facet_name, name, PARAM_DYNAMIC_TYPE)] = PARAM_DYNAMIC_TYPE_BOOL
        paramMap["%s.%s.%s.%s" %
                 (PARAM_DYNAMIC_INIT, facet_name, name,
                  PARAM_DYNAMIC_VAL)] = ','.join([val and "true" or "false" for val in vals])
      for name, vals in initParams.int_map.iteritems():
        paramMap["%s.%s.%s.%s" %
                 (PARAM_DYNAMIC_INIT, facet_name, name, PARAM_DYNAMIC_TYPE)] = PARAM_DYNAMIC_TYPE_INT
        paramMap["%s.%s.%s.%s" %
                 (PARAM_DYNAMIC_INIT, facet_name, name,
                  PARAM_DYNAMIC_VAL)] = ','.join([str(val) for val in vals])
      for name, vals in initParams.long_map.iteritems():
        paramMap["%s.%s.%s.%s" %
                 (PARAM_DYNAMIC_INIT, facet_name, name, PARAM_DYNAMIC_TYPE)] = PARAM_DYNAMIC_TYPE_LONG
        paramMap["%s.%s.%s.%s" %
                 (PARAM_DYNAMIC_INIT, facet_name, name,
                  PARAM_DYNAMIC_VAL)] = ','.join([str(val) for val in vals])
      for name, vals in initParams.string_map.iteritems():
        paramMap["%s.%s.%s.%s" %
                 (PARAM_DYNAMIC_INIT, facet_name, name, PARAM_DYNAMIC_TYPE)] = PARAM_DYNAMIC_TYPE_STRING
        paramMap["%s.%s.%s.%s" %
                 (PARAM_DYNAMIC_INIT, facet_name, name,
                  PARAM_DYNAMIC_VAL)] = ','.join(vals)
      for name, vals in initParams.byte_map.iteritems():
        paramMap["%s.%s.%s.%s" %
                 (PARAM_DYNAMIC_INIT, facet_name, name, PARAM_DYNAMIC_TYPE)] = PARAM_DYNAMIC_TYPE_BYTEARRAY
        paramMap["%s.%s.%s.%s" %
                 (PARAM_DYNAMIC_INIT, facet_name, name,
                  PARAM_DYNAMIC_VAL)] = ','.join([str(val) for val in vals])
      for name, vals in initParams.double_map.iteritems():
        paramMap["%s.%s.%s.%s" %
                 (PARAM_DYNAMIC_INIT, facet_name, name, PARAM_DYNAMIC_TYPE)] = PARAM_DYNAMIC_TYPE_DOUBLE
        paramMap["%s.%s.%s.%s" %
                 (PARAM_DYNAMIC_INIT, facet_name, name,
                  PARAM_DYNAMIC_VAL)] = ','.join([str(val) for val in vals])

    if req.groupby:
      paramMap[PARAM_GROUP_BY] = req.groupby
    if req.max_per_group > 0:
      paramMap[PARAM_MAX_PER_GROUP] = req.max_per_group

    return urllib.urlencode(paramMap)
    
  def doQuery(self, req=None):
    paramString = None
    if req:
      paramString = SenseiClient.buildUrlString(req)
    logger.info(paramString)
    urlReq = urllib2.Request(self.url,paramString)
    res = self.opener.open(urlReq)
    line = res.read()
    jsonObj = json.loads(line)
    res = SenseiResult(jsonObj)
    return res

def test_basic():
  print "==== Testing basic ====" 
  req = SenseiRequest()
  req.offset = 0
  req.count = 4

  client = SenseiClient()
  res = client.doQuery(req)
  print res.jsonMap


def testSort1():
  print "==== Testing sort1 ====" 
  req = SenseiRequest()
  req.offset = 0
  req.count = 4

  sort1 = SenseiSort("relevance")
  req.sorts = [sort1]
  
  client = SenseiClient()
  client.doQuery(req)

# XXX Sort on multiple columns Does NOT work yet
def testSort2():
  print "==== Testing sort2 ====" 
  req = SenseiRequest()
  req.offset = 0
  req.count = 4

  sort1 = SenseiSort("year", True)
  sort2 = SenseiSort("relevance")
  req.sorts = [sort1, sort2]
  
  client = SenseiClient()
  client.doQuery(req)


def testQueryParam():
  print "==== Testing query params ====" 
  req = SenseiRequest()
  req.offset = 0
  req.count = 4

  sort1 = SenseiSort("relevance")
  req.sorts = [sort1]

  qParam = {}
  qParam["query"] = "cool car"
  qParam["param1"] = "value1"
  qParam["param2"] = "value2"
  req.qParam = qParam
  
  client = SenseiClient()
  client.doQuery(req)

def testSelection():
  print "==== Testing selections ====" 
  req = SenseiRequest()
  req.offset = 0
  req.count = 3

  select1 = SenseiSelection("color", "or")
  select1.addSelection("red")
  select1.addSelection("yellow")
  select1.addSelection("black", True)
  select1.addProperty("aaa", "111")
  select1.addProperty("bbb", "222")

  select2 = SenseiSelection("price")
  select2.addSelection("[* TO 6700]")
  select2.addSelection("[10000 TO 13100]")
  select2.addSelection("[13200 TO 17300]")

  req.selections = [select1]
  client = SenseiClient()
  res = client.doQuery(req)
  print res.jsonMap

def testFacetSpecs():
  print "==== Testing facet specs ====" 
  req = SenseiRequest()
  req.query = 'moon-roof'
  req.offset = 0
  req.count = 10

  facet1 = SenseiFacet()
  facet2 = SenseiFacet(True, 1, 3, PARAM_FACET_ORDER_VAL)
  facet3 = SenseiFacet(True, 1, 3, PARAM_FACET_ORDER_VAL)

  req.facets["year"] = facet1
  req.facets["color"] = facet2
  req.facets["price"] = facet3
  req.facets["city"] = facet3
  req.facets["category"] = facet3

  sort = SenseiSort("price")
  req.sorts = [sort]
  
  client = SenseiClient()
  res = client.doQuery(req)
  # res.display()
  res.display(['year', 'color', 'tags', 'price'])
  # res.display(['bad_name'])

def testInitParams():
  print "==== Testing Facet Initialization Parameters ===="
  req = SenseiRequest()
  req.query = "moon-roof"

  param1 = SenseiFacetInitParams()
  param1.put_int_param("srcid", [12345])
  param1.put_bool_param("is_member", False)

  param2 = SenseiFacetInitParams()
  param2.put_int_param("time", 999999)
  param2.put_string_param("week", "Monday")

  req.facet_init_param_map["My-Network"] = param1
  req.facet_init_param_map["Trending"] = param2

  client = SenseiClient()
  res = client.doQuery(req)

def main():
  logger.setLevel(logging.INFO)
  formatter = logging.Formatter("%(asctime)s %(filename)s:%(lineno)d - %(message)s")
  stream_handler = logging.StreamHandler()
  stream_handler.setFormatter(formatter)
  logger.addHandler(stream_handler)

  # For Signal
  client = SenseiClient("localhost", 8421, path="sensei")

  # For cars
  # client = SenseiClient("localhost", 8080, path="sensei")

  def test_sql(stmt):
    # test(stmt)
    req = SenseiRequest(stmt)
    res = client.doQuery(req)
    res.display(req.get_columns(), 100)

  import readline
  readline.parse_and_bind("tab: complete")
  while 1:
    try:
      stmt = raw_input('> ')
      if stmt == "exit":
        break
      test_sql(stmt)
    except EOFError:
      print
      break
    except ParseException as err:
      print " "*err.loc + "^\n" + err.msg
      # print err

if __name__ == "__main__":

  main()

  # testFacetSpecs()
  # test_basic()
  # testSort1()
  # testQueryParam()
  # testSelection()
  # testInitParams()

"""
Testing Data:

select color, year, tags, price from cars where query is "cool" and color in ("gold", "green", "blue") except ("black", "blue", "yellow", "white", "red", "silver") and year in ("[1996 TO 1997]", "[2002 TO 2003]") order by price desc limit 0,10
+-------+----------------------+----------------------------------+-------------------------+
| color | year                 | tags                             | price                   |
+-------+----------------------+----------------------------------+-------------------------+
| gold  | 00000000000000001997 | cool,moon-roof,reliable,towing   | 00000000000000015000.00 |
| green | 00000000000000001996 | cool,favorite,reliable,towing    | 00000000000000015000.00 |
| green | 00000000000000001996 | cool,favorite,reliable,towing    | 00000000000000014800.00 |
| green | 00000000000000001996 | cool,moon-roof,reliable,towing   | 00000000000000014800.00 |
| green | 00000000000000002002 | automatic,cool,reliable,towing   | 00000000000000014800.00 |
| gold  | 00000000000000002002 | cool,favorite,navigation,towing  | 00000000000000014700.00 |
| gold  | 00000000000000001996 | cool,favorite,reliable,towing    | 00000000000000014700.00 |
| gold  | 00000000000000001997 | cool,favorite,reliable,towing    | 00000000000000014700.00 |
| gold  | 00000000000000001996 | cool,electric,moon-roof,reliable | 00000000000000014400.00 |
| gold  | 00000000000000001997 | cool,favorite,hybrid,reliable    | 00000000000000014200.00 |
+-------+----------------------+----------------------------------+-------------------------+
10 rows in set, 325 hits, 15001 total docs

select color, year, tags, price from cars where query is "cool" and tags contains all ("cool", "hybrid") except("favorite") and color in ("red", "yellow") order by price desc limit 0,5
+--------+----------------------+----------------------------------+-------------------------+
| color  | year                 | tags                             | price                   |
+--------+----------------------+----------------------------------+-------------------------+
| yellow | 00000000000000001995 | cool,hybrid,moon-roof,reliable   | 00000000000000014500.00 |
| red    | 00000000000000002000 | cool,hybrid,moon-roof,navigation | 00000000000000014500.00 |
| red    | 00000000000000001993 | cool,hybrid,moon-roof,navigation | 00000000000000014400.00 |
| red    | 00000000000000002002 | automatic,cool,hybrid,navigation | 00000000000000014200.00 |
| yellow | 00000000000000001999 | automatic,cool,hybrid,reliable   | 00000000000000012200.00 |
+--------+----------------------+----------------------------------+-------------------------+
5 rows in set, 132 hits, 15001 total docs

select color, year, tags, price from cars where query is "cool" and tags contains all ("cool", "hybrid") except ("favorite") and color in ("red") with ("aaa":"111", "bbb":"222") order by price desc limit 0,10 browse by (color: (true, 1, 10, hits), year: (true, 1, 10, value), price: (true, 1, 10, value))
+-------+----------------------+----------------------------------+-------------------------+
| color | year                 | tags                             | price                   |
+-------+----------------------+----------------------------------+-------------------------+
| red   | 00000000000000002000 | cool,hybrid,moon-roof,navigation | 00000000000000014500.00 |
| red   | 00000000000000001993 | cool,hybrid,moon-roof,navigation | 00000000000000014400.00 |
| red   | 00000000000000002002 | automatic,cool,hybrid,navigation | 00000000000000014200.00 |
| red   | 00000000000000001998 | automatic,cool,hybrid,navigation | 00000000000000012100.00 |
| red   | 00000000000000002002 | automatic,cool,hybrid,reliable   | 00000000000000011500.00 |
| red   | 00000000000000002002 | automatic,cool,hybrid,reliable   | 00000000000000011400.00 |
| red   | 00000000000000001998 | automatic,cool,hybrid,reliable   | 00000000000000011400.00 |
| red   | 00000000000000001996 | automatic,cool,hybrid,reliable   | 00000000000000011200.00 |
| red   | 00000000000000001999 | automatic,cool,hybrid,reliable   | 00000000000000011100.00 |
| red   | 00000000000000002001 | cool,hybrid,moon-roof,reliable   | 00000000000000010500.00 |
+-------+----------------------+----------------------------------+-------------------------+
10 rows in set, 59 hits, 15001 total docs
+-------------+
| color       |
+-------------+
| white  (73) |
| yellow (73) |
| blue   (62) |
| silver (61) |
| red    (59) |
| green  (58) |
| gold   (53) |
| black  (52) |
+-------------+
+-----------------------+
| price                 |
+-----------------------+
| [* TO 6700]      (21) |
| [10000 TO 13100] (8)  |
| [13200 TO 17300] (3)  |
| [6800 TO 9900]   (27) |
+-----------------------+
+---------------------+
| year                |
+---------------------+
| [1993 TO 1994] (16) |
| [1995 TO 1996] (13) |
| [1997 TO 1998] (10) |
| [1999 TO 2000] (9)  |
| [2001 TO 2002] (11) |
+---------------------+

select color, grouphitscount from cars group by color top 1 limit 0,16000
+--------+----------------+
| color  | grouphitscount |
+--------+----------------+
| white  | 2196           |
| yellow | 2105           |
| red    | 2160           |
| black  | 3141           |
| green  | 1085           |
| gold   | 1110           |
| blue   | 1104           |
| silver | 2100           |
+--------+----------------+
8 rows in set, 15001 hits, 15001 total docs

Note: (= (+ 2196 2105 2160 3141 1085 1110 1104 2100) 15001)

select uid, color, makemodel from cars group by color top 3 limit 0,4
=========================================
| uid | color  | makemodel              |
=========================================
| 1   | white  | asian/acura/1.6el      |
| 2   | white  | asian/acura/1.6el      |
| 3   | white  | asian/acura/1.6el      |
+-----+--------+------------------------+
| 0   | yellow | asian/acura/1.6el      |
| 244 | yellow | european/bentley/azure |
| 245 | yellow | european/bentley/azure |
+-----+--------+------------------------+
| 242 | red    | european/bentley/azure |
| 246 | red    | european/bentley/azure |
| 247 | red    | european/bentley/azure |
+-----+--------+------------------------+
| 241 | black  | european/bentley/azure |
| 243 | black  | european/bentley/azure |
| 10  | black  | asian/acura/3.2tl      |
+-----+--------+------------------------+
=========================================
4 groups in set, 15001 hits, 15001 total docs

// Signal search example
select tags, publicShareFlag, userid, country, updateType from signal where country in ("us") and My-Network in ("1", "2") given facet param (My-Network, "srcid", int, "8233570")

"""
