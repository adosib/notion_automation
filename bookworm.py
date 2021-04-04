from settings import (
    client, 
    cfg, 
    ARTICLES_ID, 
    BOOKS_ID, 
    READING_LOG_ID,
    LAST_SNAPSHOT
)
from datetime import datetime 
import pandas as pd
import numpy as np

if __name__ == "__main__":
    reading_page_block = client.get_block(cfg['reading'])

    books = {
        'name': [],
        'identifier': [],
        'pages_read': [],
        'timestamp': []
    }

    timestamp = datetime.now()

    # for each book or article, capture the desired fields
    for block in reading_page_block.children:
        if block.id not in [ARTICLES_ID, BOOKS_ID]:
            continue
        else:
            for row_block in block.collection.get_rows():
                if row_block.title:
                    books['name'].append(row_block.title)
                    try:
                        books['pages_read'].append(row_block.page_number or 0)
                    except AttributeError:
                        # articles don't have the pages_read property
                        if row_block.status and row_block.status.lower()=="read":
                            books['pages_read'].append(1)
                        else:
                            books['pages_read'].append(0)
                    books['identifier'].append(row_block.id)
                    books['timestamp'].append(timestamp) 

    reading_list = pd.DataFrame(books)
    last_snapshot = pd.read_csv(LAST_SNAPSHOT)

    merged = reading_list.merge(
        last_snapshot, how='left', on="identifier", suffixes=("_current", "_prior")
    )
    merged['page_diff'] = merged['pages_read_current'] - \
        merged['pages_read_prior'].replace({np.nan: 0})
    # want to log records that had progress
    to_log = merged.loc[merged['page_diff']>0]
    
    reading_log = client.get_block(READING_LOG_ID) # child to reading_page_block

    # add records to the reading log
    for entry in to_log.itertuples():
        row = reading_log.collection.add_row()
        row.title = entry.name_current
        
        object_ref = client.get_block(entry.identifier)
        if object_ref.parent.parent.id == BOOKS_ID:
            row.book = client.get_block(entry.identifier)
        elif object_ref.parent.parent.id == ARTICLES_ID:
            row.article = client.get_block(entry.identifier)
            
        row.pages_read = entry.page_diff 
        row.timestamp = entry.timestamp_current
    
    # write the current reading list to the snapshot file
    reading_list.to_csv(LAST_SNAPSHOT)