#!/usr/bin/env python3
# coding=utf-8

from config import *

import boto3
import hashlib
import base64
import requests
# import json

# import nacl.secret
# from nacl.public import Box as BoxNaCl
# from nacl.encoding import Base64Encoder

class S3_CONNECT():
    def __init__(self,bucket,accessKeyID,accessKeySecret):
        self.s3 = boto3.client(  
            's3',  
            aws_access_key_id= accessKeyID,  
            aws_secret_access_key= accessKeySecret
        )
        self.bucket = bucket

    def S3_upload(self,filestr,filename, MIME):
        md5 = hashlib.md5()
        md5.update(bytes(filestr, encoding='utf-8'))

        resp = self.s3.put_object(Bucket=self.bucket, Key=filename, Body=filestr, ContentType=MIME, ContentMD5=base64.b64encode(md5.digest()).decode('utf-8'))

        if not md5.hexdigest() in resp['ETag']:
            print(resp)


# def SharedEncrypt(box, plaintext):
#     plaintext = bytes(plaintext, encoding='utf-8')
#     nonce = nacl.utils.random(BoxNaCl.NONCE_SIZE)
#     ciphertext = box.encrypt(plaintext, nonce, encoder=Base64Encoder)
#     nonce = ciphertext.nonce
#     ciphertext = ciphertext.ciphertext
#     return ciphertext.decode('utf-8'), nonce.decode('utf-8')

# def SharedDecrypt(box, ciphertext, nonce):
#     nonce = Base64Encoder.decode(nonce)
#     plaintext = box.decrypt(ciphertext, nonce, encoder=Base64Encoder)
#     return plaintext.decode('utf-8')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['upload', 'download'])
    # parser.add_argument('--password', default="Yellow_Submarine")
    parser.add_argument('--bucket', default="columbus-config-qa02")
    parser.add_argument('--ak')
    parser.add_argument('--sk')
    parser.add_argument('--website', default="http://columbus-config-qa02.s3-website-us-west-1.amazonaws.com")

    args = parser.parse_args()

    # SharedKey = bytes(args.password.zfill(32), encoding='utf-8')
    # box = nacl.secret.SecretBox(bytes(SharedKey))

    if args.action == 'upload':
        with open(deploy_config_path,'r') as f:
            plaintext = f.read()
        # ciphertext, nonce = SharedEncrypt(box, plaintext)

        # body = {
        #     "payload": ciphertext,
        #     "nonce": nonce
        # }

        S3C = S3_CONNECT(args.bucket, args.ak, args.sk)
        # S3C.S3_upload(json.dumps(body, indent=4), "columbus_config.json")
        S3C.S3_upload(plaintext, "columbus_config.json", "application/json")

    if args.action == 'download':
        r = requests.get(args.website)
        # ciphertext = r.json()['payload']
        # nonce = r.json()['nonce']
        # plaintext = SharedDecrypt(box, ciphertext, nonce)
        plaintext = r.text
        with open(deploy_config_path,'w') as f:
            f.write(plaintext)