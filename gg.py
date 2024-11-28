from time import sleep
from requests import session
from pprint import pprint
s=session()


a = s.get('https://labcoat.medicalboard.co/api/courses/dor-alashaa-oaltsoyr-altby/lecture/41').json()
# pprint(a['data']['course']['sections'])
for x in a['data']['course']['sections']:
	# 
	for i in x['items']:
		try:
			print( f"{i['title']['en']}" )
			a = open(f"{i['title']['en']}.mp4",'wb')
			a.write(s.get(i['video_url']).content)
		except Exception as e:
			print(str(e))
