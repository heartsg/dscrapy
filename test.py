import sys
sys.path.append('/home/hearts/source/dscrapy/')

import dscrapy.settings

dsettings = dscrapy.settings.DScrapySettings()

print dsettings.getint('CONCURRENT_ITEMS')
