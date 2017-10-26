#!/usr/bin/Python
import os
from ghost import Ghost
gh = Ghost()
with gh.start() as session:
    page, extra_resources = session.open("http://index.baidu.com/?tpl=crowd&word=hello", timeout=30, headers={"Cookie":"earchtips=1; bdshare_firstime=1472540844339; BAIDUID=CE1543C3C86B079F8CBB68B33D44C872:FG=1; BIDUPSID=C14D006D7C72FDA7711A079E6A65CC4A; PSTM=1484843465; BDSFRCVID=J50sJeCCxG36inTiwqsVDP8_QCweuWgL9Fsp3J; H_BDCLCKID_SF=JRAjoK-XJDv8fJ6xq4vhh4oHjHAX5-RLf2LtoPOF5lOTJh0Rj4r_3-FWKqbp0p8OXa6mLb5aQb3dbqQRK5bke4tX-NFtt68JJU5; MCITY=-340%3A; CHKFORREG=5fee3ec1f4bdf3e28e2d825b15574023; PSINO=6; H_PS_PSSID=1429_19034_21118_21929_22035_22176_20927; BDUSS=c4aWxqbUtQbkcxWDBEUWRjNFZuTXE4ZURyeVFlbTJyUDNtdXFtaXYwNmRtdUJZSVFBQUFBJCQAAAAAAAAAAAEAAAABwsUpZ2lraWVuZwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJ0NuVidDblYcF; Hm_lvt_d101ea4d2a5c67dab98251f0b5de24dc=1488442015; Hm_lpvt_d101ea4d2a5c67dab98251f0b5de24dc=1488522657"})
    #session.capture_to("test.png")
    print page.content
    #assert page.http_status == 200 and 'jeanphix' in page.content