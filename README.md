# torrentpython
A python client that downloads torrents from CLI



# references

https://blog.jse.li/posts/torrent/  
https://wiki.theory.org/BitTorrent_Tracker_Protocol  
https://wiki.theory.org/BitTorrentSpecification#Tracker_Request_Parameters  
https://www.cs.swarthmore.edu/~aviv/classes/f12/cs43/labs/lab5/lab5.pdf  
https://allenkim67.github.io/programming/2016/05/04/how-to-make-your-own-bittorrent-client.html  



http://www.dsc.ufcg.edu.br/~nazareno/bt/bt.htm


explains about protocol use, what to expect from the messages and possible codes



### how to implement the tracker response
https://wiki.theory.org/BitTorrentSpecification#Tracker_Response




### Entender o formato de handshake

https://github.com/gallexis/PyTorrent/blob/master/message.py


### Big Endian vs Little Endian

Can use struct Module to apply format and parse network conn.

```
import struct
struct.pack(">h", 1023)
# b'\x03\xff`
struct.pack("<h", 1023)
# b'\xff\x03`
```
### asyncio way to implement
https://stackoverflow.com/questions/48506460/python-simple-socket-client-server-using-asyncio
