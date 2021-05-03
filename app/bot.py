#!/usr/bin/python

import mattermost
import mattermost.ws
import pprint
import websocket
import json
import os
import cv2

try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract


try:
    import thread
except ImportError:
    import _thread as thread

# login
# Pegas as variáveis de acesso do ambiente

mmURL = os.getenv('MM_URL')
mmAPIKey = os.getenv("MM_API_KEY")
mmWebsocketURL = os.getenv("MM_WEBSOCKET_URL")
language = os.getenv("TLANG")
tesseract_conf = os.getenv("TESERACT_CONF")
debug = True

#Conecta no servidor
mm = mattermost.MMApi(mmURL)
mm.login(bearer=mmAPIKey)

#Define configuracoes do tesseract
#custom_oem_psm_config = r'--oem 1 --psm 12'
custom_oem_psm_config = tesseract_conf

def on_message(ws, message):
    msgobj = json.loads(message)
    if ( msgobj['event'] == "posted" ) and ( msgobj['data']['sender_name'] != "@imagebot" ):
        if (msgobj['data']['image'] == 'true'):
           print ("tem imagem\n" )
           post = json.loads(msgobj['data']['post'])
           if (debug):
              pprint.pprint(post)
              pprint.pprint(post['file_ids'])
           metadata = post['metadata']['files']
           for fileobj in metadata:
               r = mm.get_file(fileobj['id'])
               filename = "/opt/app/data/"+fileobj['id']+"."+fileobj['extension']
               with open(filename, "wb") as f:
                  f.write(r.content)
               # Usa biblioteca de imagens opencv para limpar ruidos e melhorar o tratamento do tesseract
               image = cv2.imread(filename)
               gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
               gray = cv2.threshold(gray, 0, 255,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
               #gray =  cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV|cv2.THRESH_OTSU,3,0)
               cv2.imwrite(filename, gray)
               # Converte a imagem tratada em texto
               mensagem = pytesseract.image_to_string(Image.open(filename), lang=language,config=custom_oem_psm_config)
               if (debug): 
                  print("MENSAGEM "+mensagem)
               # monta a resposta para o interlocutor
               mm.create_post(msgobj['broadcast']['channel_id'],mensagem)
               #remove o arquivo limpo
               os.remove(filename)

        else:
           resposta = "Oi " + msgobj['data']['sender_name'] + " recebi: " + json.loads(msgobj['data']['post'])['message'] + " no que posso ajudar?" 
           mm.create_post(msgobj['broadcast']['channel_id'],resposta)

def on_error(ws, error):
    pprint.pprint(error)

def on_close(ws):
    print("### closed ###")

if __name__ == "__main__":
    websocket.enableTrace(True)
    header = [ "Authorization: Bearer "+mmAPIKey, "Origin: mm.ginglass.com.br" ]
    ws = websocket.WebSocketApp(mmWebsocketURL,
                              header = header,
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)

    ws.run_forever()
