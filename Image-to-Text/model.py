import requests
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large").to("cuda")

img_url = 'https://cdn.discordapp.com/attachments/1166126970845806683/1268597791966367929/GT0P1sjXwAAP_kT.png?ex=66b2f003&is=66b19e83&hm=1523afea4e7d55866fdbd2ec5dc02bb6d74a833aa99c4cfa7897c81cb09b513b&' 
raw_image = Image.open(requests.get(img_url, stream=True).raw).convert('RGB')

# conditional image captioning
text = "a photography of"
inputs = processor(raw_image, text, return_tensors="pt").to("cuda")

out = model.generate(**inputs, max_new_tokens=300000)
print(processor.decode(out[0], skip_special_tokens=True))

# unconditional image captioning
inputs = processor(raw_image, return_tensors="pt").to("cuda")

out = model.generate(**inputs, max_new_tokens=300)
print(processor.decode(out[0], skip_special_tokens=True))