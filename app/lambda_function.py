import urllib.parse
import boto3
from PIL import Image
from os.path import basename
from os.path import splitext

s3 = boto3.client('s3')


def lambda_handler(event, context):
    # print("Received event: " + json.dumps(event, indent=2))

    bucket = event['Records'][0]['s3']['bucket']['name']
    original_image_path = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    original_image = basename(original_image_path)
    source_image_path = '/tmp/' + original_image

    try:
        s3.download_file(bucket, original_image_path, source_image_path)
    except Exception as e:
        print(e)
        print('Error downloading object {} from bucket {}.'.format(source_image_path, bucket))
        raise e

    for image_format in ['png', 'gif', 'bmp']:
        try:
            source_image = basename(source_image_path)
            filename, extension = splitext(source_image)
            tmp_image_path = '/tmp/{}.{}'.format(filename, image_format)
            convert_image(source_image_path, tmp_image_path)
            destination_image_path = '{}/{}.{}'.format(image_format, filename, image_format)
            s3.upload_file(tmp_image_path, bucket, destination_image_path)
            print('File was converted and uploaded')
        except Exception as e:
            print(e)
            print('Error converting object {} from bucket {} to {} format'
                  .format(source_image_path, bucket, image_format))


def convert_image(source_image_path, destination_image_path):
    with Image.open(source_image_path) as original_image:
        original_image.save(destination_image_path)
