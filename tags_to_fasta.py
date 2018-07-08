#!/bin/env python2.7
#
# read tag info from stdin and write out as
# fasta, repeating each sequence as per tag count
#
#    The tag count file contains records like
#TGCAGAAGTCTTGAATTTAATTCAGGATACTCGTCTACCACGTTGTCCATGTCTCCGCAAGGGA        64      1
#TGCAGAAGTCTTGAATTTAGTTCAGGATACTCGTCTACCACGTTGTCCATGTCTCCGCAAAGGA        64      1
#TGCAGAAGTCTTGGCCTGAGGAGCTGAGTTGTGCATCACCCTGCAAAAAAAAAAAAAAAAAAAA        45      3
#TGCAGAAGTCTTGGTGATGTTGTAAAGGTGTGTTGATGTCTCTGTGGTTGAGGACACATCATCA        64      3
#
# example : 
#./cat_tag_count.sh /dataset/hiseq/scratch/postprocessing/151016_D00390_0236_AC6JURANXX.gbs/SQ0124.processed_sample/uneak/tagCounts/G88687_C6JURANXX_1_124_X4.cnt | ./tags_to_fasta.py
# 


import sys
import re
import itertools
import argparse
import random


def getSampleBool(samplerate):
    # sample from bernoulli p=1/samplerate  if we are sampling, or if not return 1
    if samplerate is None:
      return 1
    elif samplerate <= 0:
      return 1
    elif samplerate >= 1.0:
      return 1
    else:
      uniform = random.random()
      if uniform <= samplerate:
         return 1
      else:
         return 0

def tags_to_fasta(options):
    print options
    tag_iter = (record for record in sys.stdin)
    tag_iter = (re.split("\s+",record.strip().upper()) for record in tag_iter)    # parse the 3 elements 
    tag_iter = ((my_tuple[0], int(my_tuple[1]), int(my_tuple[2]))  for my_tuple in tag_iter if len(my_tuple) == 3)  # skip the header and make ints
    #tag_iter = (my_tuple[0][0:my_tuple[1]] for my_tuple in tag_iter)  # use the tag-length to substring the tag then throw away the numbers
    #tag_iters = (  itertools.repeat(  (my_tuple[0][0:my_tuple[1]],my_tuple[2]) , my_tuple[2]) for my_tuple in tag_iter)  # use the tag-length to substring the tag then throw away the numbers
    if not options["unique"]:
        tag_iters = (  itertools.repeat(  my_tuple[0][0:my_tuple[1]]  , my_tuple[2]) for my_tuple in tag_iter)  # use the tag-length to substring the tag then throw away the numbers
    else:
        tag_iters = (  itertools.repeat(  ( my_tuple[0][0:my_tuple[1]], my_tuple[2])  , 1) for my_tuple in tag_iter)
    seq_number = 1
    for tag_iter in tag_iters:
        for tag in tag_iter:
            if options["samplerate"] is None:
                if options["unique"]:
                    print ">seq_%d count=%d"%(seq_number,tag[1])
                    print tag[0]
                else:
                    print ">seq_%d"%seq_number
                    print tag
                seq_number += 1
            else:
                if getSampleBool(options["samplerate"]) == 1:
                    if options["unique"]:
                        print ">seq_%d count=%d"%(seq_number,tag[1])
                        print tag[0]
                    else:
                        print ">seq_%d"%seq_number
                        print tag
                seq_number += 1
                    

def get_options():
    description = """
    This script outputs tags from stdin as fasta on stdout, optionally
    outputting each tag tag_count times (that is the defult)
    """
    
    long_description = """
    Example :

./cat_tag_count.sh /dataset/hiseq/scratch/postprocessing/151016_D00390_0236_AC6JURANXX.gbs/SQ0124.processed_sample/uneak/tagCounts/G88687_C6JURANXX_1_124_X4.cnt | ./tags_to_fasta.py

    """
    parser = argparse.ArgumentParser(description=description, epilog=long_description, formatter_class = argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-u', '--unique' , dest='unique', action='store_true', help="list unique tags")
    parser.add_argument('-s', '--samplerate', dest='samplerate', type=float, metavar='sample rate', default = None, help="specify a random sampling rate - e.g. .1 means randomly sample around 10%% etc.")

    args = vars(parser.parse_args())

    random.seed()

    return args


def main():
    tags_to_fasta(get_options())
    return 

    
if __name__ == "__main__":
   main()
        




