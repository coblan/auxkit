def findone(collection,dc):
    for doc in collection:
        find=True
        for k,v in dc.items():
            if doc.get(k)!=v:
                find=False
        if find:
            return doc