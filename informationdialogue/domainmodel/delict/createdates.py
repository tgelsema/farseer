#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 10:15:48 2019

@author: tgelsema
"""

dageninmaand = {
        1: 31,
        2: 29,
        3: 31,
        4: 30,
        5: 31,
        6: 30,
        7: 31,
        8: 31,
        9: 30,
        10: 31,
        11: 30,
        12: 31
}

def createdates():
    i = 0
    fw = open("datums.txt", "w")
    for m in dageninmaand.keys():
        d = 1
        while d <= dageninmaand[m]:
            writedaginmaand(i, m, d, fw)
            i += 1
            d += 1

def writedaginmaand(i, m, d, fw):
    fw.write('\t'.join([str(i), str(m), str(d)]))
    fw.write('\n')