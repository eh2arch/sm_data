#x -*- coding: utf-8 -*-

import time
import json
import sys
from tasks import collectFromInstagram
import time

from metaData import instagramTokens, circleCentres


def collectData(accessToken, listOfCoordinates):

	for centre in listOfCoordinates:
                print accessToken, centre
		collectFromInstagram.delay(accessToken, centre[0], centre[1])


if __name__ == "__main__":

	while True:
		
		for i in range(7):
			collectData(instagramTokens[i], circleCentres[i * 4 : (i + 1) * 4])

		time.sleep(4)

