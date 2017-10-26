#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time

import nlp_pb2
import grpc
channel = grpc.insecure_channel("cs4:51051")
stub = nlp_pb2.NlpStub(channel)
line="广东省东莞市中级人民法院\t民事裁定书\t（\t2014\t）东中法立民终字第\t36\t号\t上诉人（原审\t被告\t）\t：\t东莞市莞香苑建造有限公司\t(\t以下简称莞香苑公司\t)\t，住所东莞市南城区胜和路金盈大厦主楼第\t11\t层\t1101\t室，注册号为\t441900000061520\t。\t法定代表人：刘永泉。\t委托代理人：郭安慧，广东林德律师事务所律师。\t委托代理人：张木超，广东林德律师事务所律师助理。\t被上诉人（原审\t原告\t）\t：\t曾燕文，男。\t委托代理人：陈进，广东大洲律师事务所律师。\t委托代理人：张素萍，广东大洲律师事务所辅助人员。\t被上诉人（原审\t原告\t）\t：\t李伟容，女。\t委托代理人：陈进，广东大洲律师事务所律师。\t委托代理人：张素萍，广东大洲律师事务所辅助人员。\t上诉人\t莞香苑公司\t不服东莞市第一人民法院（\t2013\t）东一法民一初字第\t10162\t号\t民事裁定，向本院提起上诉称：\t上诉人与被上诉人在发生本案的商品房预售合同纠纷后，双方进行了多次沟通和协商，被上诉人为了快速解决纠纷，在纠纷处理的解决方式上与上诉人达成一致意见，双方同意若协商不成，则将该纠纷交由广州仲裁委员会东莞分会进行仲裁。因此请求依法将本案移送至广州仲裁委员会东莞分会进行仲裁。\t被上诉人\t曾燕文、李伟容\t未\t答辩。\t本院认为，\t本案系商品房预售合同纠纷。由于上诉人与被上诉人签订的《商品房买卖合同》第十九条明确约定了“在履行合同中发生争议，协商不成的依法向人民法院起诉”。依据《中华人民共和国民事诉讼法》第二十三条“因合同纠纷提起的诉讼，由被告住所地或者合同履行地人民法院管辖”的规定，本案原审被告莞香苑公司住所地及原审原、被告合同履行地均在东莞市南城区，属于原审法院管辖范围，原审法院依法对本案具有管辖权。上诉人莞香苑公司提出“被上诉人\t在纠纷处理的解决方式上与上诉人达成一致意见，双方同意若协商不成，则将该纠纷交由广州仲裁委员会东莞分会进行仲裁”的上诉理由，经查，上诉人\t未提供任何证据证明，且在一审时原审原告对此否认。因此，此上诉理由不能成立，本院不予采信。\t原审裁定驳回上诉人的管辖权异议正确，本院予以维持。依照《中华人民共和国民事诉讼法》第一百六十九条、第一百七十一条、第一百七十五条的规定，裁定如下：\t驳回上诉，维持原裁定。\t本裁定为终审裁定。\t审\t\t判\t\t长\t\t杜新春\t审\t\t判\t\t员\t\t贾鸿宾\t代理审判员\t\t王九龙\t二○一四年二月十日\t\t书\t\t记\t\t员\t\t李丽欢"
#response = stub.WordSegment(nlp_pb2.SentenceRequest(sentence=line))
#print("Client received: " + response.message)
#response = stub.PosTag(nlp_pb2.SentenceRequest(sentence=line))
#print("Client received: " + response.message)
time1=time.time()
response = stub.EventExtract(nlp_pb2.SentenceRequest2(sentence1="judge_wenshu",sentence2=line))
print("Client received: " + response.message)
print time.time()-time1
