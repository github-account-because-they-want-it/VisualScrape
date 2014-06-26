'''
Created on Jun 18, 2014
@author: Mohammed Hamdy
'''

import csv, json, os, codecs

class FileExporter(object):
  """Totally ignores encoding"""
  FORMAT_CSV = "CSV"
  FORMAT_JSON = "JSON"
  FORMATS_AVAILABLE = [FORMAT_CSV, FORMAT_JSON]
  ENCODING = "utf-8"
  ENCODING_FALLBACK = "latin-1"
  @classmethod  
  def export(cls, data, fname, folder, fmt):
    """
    Args:
         data: a list of dictionaries where the keys are column names
         fname: the file name to export to without extension"""
    assert fmt in cls.FORMATS_AVAILABLE, "Unsupported export format: <{}>".format(fmt)
    from visualscrape.ui.viewer.dialog import AlreadyExistsDialog
    output = os._spider_path.normpath(os._spider_path.join(folder, fname))
    if os._spider_path.exists(output):
      dialog = AlreadyExistsDialog(output)
      dialog.exec_()
      if dialog.ret == dialog.CANCEL: return # user retracted from this export
    if fmt == cls.FORMAT_CSV: output = output + ".csv"
    elif fmt == cls.FORMAT_JSON: output = output + ".json"
    with codecs.open(output, "wb", encoding=cls.ENCODING) as fo:
      if not len(data): return
      data = cls.decode_data(data)
      if fmt == cls.FORMAT_CSV:
        csv_writer = csv.DictWriter(fo, fieldnames=cls.longest_dct(data).keys(), extrasaction="ignore")
        csv_writer.writeheader()
        for row in data: 
          csv_writer.writerow(row)
      elif fmt == cls.FORMAT_JSON:
        json.dump(data, fo, ensure_ascii=False)
        
  @classmethod
  def export_all(cls, data, fnames, folder, fmt):
    for f in fnames:
      cls.export(data, f, folder, fmt)
      
  @classmethod
  def decode_data(cls, data):
    decoded = []
    decoded_row = {}
    for row in data:
      for k, v in row.items():
        if isinstance(k, str):
          k = cls.decode_entity(k)
        if isinstance(v, str):
          v = cls.decode_entity(v)
        decoded_row[k] = v
      decoded.append(decoded_row)
      decoded_row = {}
    return decoded
  
  @classmethod
  def decode_entity(cls, entity):
    try:
      return entity.decode(cls.ENCODING)
    except UnicodeDecodeError as ex:
      return entity.decode(cls.ENCODING_FALLBACK)
    
  @classmethod
  def longest_dct(cls, data):
    """Include the maximum number of keys in the result"""
    longest = None
    top_length = 0
    for dct in data:
      dct_len = len(dct)
      if dct_len > top_length:
        top_length = dct_len
        longest = dct
    return longest