from ast import arg
from numpy import Infinity
from pyparsing import (
    Word,
    alphanums,
    Keyword,
    Group,
    Forward,
    Suppress,
    OneOrMore,
    oneOf,
)

import re, os, sys
sys.path.insert(0, './QueryParser')
# from Querying import DBQuery as dbq

from Querying import preprocess # import preprocess

import pickle

# SONGCOUNT = 1200000
# LYRICCOUNT = 60000000

class QueryParser:
    def __init__(self):
       
        self._methods = {
            "and": self.evaluateAnd,
            "or": self.evaluateOr,
            "not": self.evaluateNot,
            "parenthesis": self.evaluateParenthesis,
            "phrase": self.evaluatePhrase,
            "proximity": self.evaluateProximity,
            "word": self.evaluateWord
        }

        # self.connection = dbq.DBQuery()
        # self.songCount = self.connection.countSongs()
        # self.lyricCount = self.connection.countLyrics()

        self.songCount = 1300000
        self.lyricCount = 60000000
        self._parser = self.parser()
        self.text = ""
        self.words = []
        self.isSong = True

    def parser(self):
        """
        This function returns a parser.
        Grammar:
        - a query consists of alphanumeric words
        - a sequence of words between quotes is a phrase search
        - words can be used together by using operators ('&&', '||', '~')
        - words with operators can be grouped with parenthesis
        - phrase or proximity search can be preceded by a 'not' operator
        """
        operatorOr = Forward()

        alphabet = alphanums + ' '

        notKeyword = Keyword("~") 

        andKeyword = Keyword("&&")

        orKeyword = Keyword("||")

        operatorWord = Group(Word(alphabet)).setResultsName("word")

        operatorBooleanContent = Forward()

        operatorBooleanContent << ((operatorWord + operatorBooleanContent) | operatorWord)

        operatorPhrase = (
            Group(Suppress('"') + operatorBooleanContent + Suppress('"')).setResultsName(
                "phrase"
            )
            | operatorWord
        )

        operatorProximity = (
            Group(Suppress('#(') + operatorBooleanContent + Suppress(',') + operatorBooleanContent +  Suppress(',') + operatorBooleanContent + Suppress(')')).setResultsName(
                "proximity"
            )
            | operatorWord
        )

        operatorParenthesis = (
            Group(Suppress("(") + operatorOr + Suppress(")")).setResultsName(
                "parenthesis"
            )
            | operatorPhrase | operatorProximity
        )


        operatorNot = Forward()
        operatorNot << (
            Group(Suppress(notKeyword) + operatorNot).setResultsName(
                "not"
            )
            | operatorParenthesis
        )

        operatorAnd = Forward()
        operatorAnd << (
            Group(
                operatorNot + Suppress(andKeyword) + operatorAnd
            ).setResultsName("and")
            | operatorNot
        )

        operatorOr << (
            Group(
                operatorAnd + Suppress(orKeyword) + operatorOr
            ).setResultsName("or")
            | operatorAnd
        )

        return operatorOr.parseString

    def evaluateAnd(self, argument):


        clause_results = [self.evaluate(arg) for arg in argument]

        assert(len(clause_results) == 2)

        return ['a',clause_results[0],clause_results[1]]


    def evaluateOr(self, argument):
      
        clause_results = [self.evaluate(arg) for arg in argument]

        assert(len(clause_results) == 2)

        return ['o',clause_results[0],clause_results[1]]
        

        
        
        # clause_results = [self.evaluate(arg) for arg in argument]
    
        # clause_doc_ids = [[elm[0] for elm in clause] for clause in clause_results]
        
        # doc_ids = set.union(*map(set,clause_doc_ids))

        # scores = {doc_id : 0 for doc_id in doc_ids}

        # for clause in clause_results:
        #     for id, score in clause:
        #         if id in doc_ids and score > scores[id]:
        #             scores[id] = score

        # return [(doc_id,scores[doc_id]) for doc_id in scores]

    def evaluateNot(self, argument):

        if(self.isSong):
            count = self.songCount
        else:
            count = self.lyricCount

        return ['n',count,self.evaluate(argument[0])]

    def evaluateParenthesis(self, argument):

        if len(argument) > 1:
            raise BaseException("?")

        return self.evaluate(argument[0])

    def evaluatePhrase(self, argument):
        
        # Phrase search 

        terms = list(list(zip(*preprocess.preprocess(argument[0][0])[0]))[0])

        return ["p",terms,self.isSong]

    def evaluateProximity(self, argument):
        
        # Proximity search 

        # print("proximity")

        if(len(argument) != 3):
            raise BaseException("??")

        try:
            distance = int(argument[0][0])
        except:
            raise BaseException("Proximity distance is not an int")

        term1 = argument[1][0].strip()
        term2 = argument[2][0].strip()

        if(any(term.count(' ') for term in [term1,term2])):
            raise BaseException("Proximity terms must be single words")

        # print("distance : " + str(distance))
        # print("term1 : " + str(term1))
        # print("term2 : " + str(term2))

        term1 = preprocess.preprocess(term1)[0][0][0]
        term2 = preprocess.preprocess(term2)[0][0][0]
        
        proximity = distance
        isSong = self.isSong

        return ["x",term1, term2, proximity, isSong]



    def evaluateWord(self, argument):

        # Do search over argument
        searchReturn = True


        terms = list(list(zip(*preprocess.preprocess(argument[0])[0]))[0])
        isSong = self.isSong

        return ["b",terms,isSong]


    def evaluate(self, argument):
        
        # print("evaluate")
        # print(argument)

        return self._methods[argument.getName()](argument)

    def Parse(self, query):

        return self.evaluate(self._parser(query)[0])

    def parseQuery(self, expr, isSong):

        print("exprrr")

        self.isSong = isSong

        # # get top N results (skipping the first `skip` results)
        # # return a list of (id, score) tuples, sorted from highest to lowest by score (e.g. [(19, 1.5), (6, 1.46), ...]
        # print(self.Parse(expr))

        # print("qp done")
        
        return self.Parse(expr)

        
# NOTE: This is only used for testing the local file itself
#x = QueryParser()

# # x.query('! bean', True)
#x.query('"nowhere left to run" && #(20, Thriller, Killer)', True)
#x.query("push",True)
# # x.query('! bean', True)
#x.query('"nowhere left to run" && #(20, Thriller, Killer)', True)
