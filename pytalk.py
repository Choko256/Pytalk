#-*- coding:utf-8 -*-

# ###################################### #
#     PYTALK 									#
# ###################################### #
#  This software is OPEN SOURCE and FREE	#
#	If you paid to get theses sources,	#
#	 go to get reimbursed !					#
# ###################################### #
#  GNU/GPL License V.3						#
#  Created by ChakSoft Computing.			#
#  Date: 2013-03-12							#
# ###################################### #

import os
import sys
from gui import mgr

def pytalk():
	mgr.GUIManager.create_main_window()
	
if __name__ == "__main__":
	pytalk()
