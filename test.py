maxlen = 0
for i in (['name', 'year','authors', 'genres', 'width', 'height', 'book_type', 'source', 'date_added', 'date_read', 'rating']):
    if len(i) > maxlen: maxlen = len(i)
print(maxlen)