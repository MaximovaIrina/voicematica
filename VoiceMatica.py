from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from speechbrain.pretrained import EncoderClassifier
import torch.nn.functional as F
import torch, torchaudio
import warnings
warnings.filterwarnings("ignore")

class VoiceMatica:
    MODEL   = "microsoft/speecht5_tts"              # https://huggingface.co/microsoft/speecht5_tts
    VOCODER = "microsoft/speecht5_hifigan"          # https://huggingface.co/microsoft/speecht5_tts
    ENCODER = "speechbrain/spkrec-xvect-voxceleb"   # https://huggingface.co/datasets/Matthijs/cmu-arctic-xvectors

    def __init__(self):
        self.processor  = SpeechT5Processor.from_pretrained(self.MODEL)
        self.model      = SpeechT5ForTextToSpeech.from_pretrained(self.MODEL)
        self.vocoder    = SpeechT5HifiGan.from_pretrained(self.VOCODER)
        self.encoder    = EncoderClassifier.from_hparams(self.ENCODER)
        
    def _file_to_embed(self, file):
        embed = None
        if file.endswith('.pt'):
            embed = torch.load(file)
        else:
            audio, fs = torchaudio.load(file)
            audio = torchaudio.functional.resample(audio, orig_freq=fs, new_freq=16000)
            embed = self.encoder.encode_batch(audio)
            embed = F.normalize(embed, dim=2)[0]
        return embed
    
    def __call__(self, text, file):
        with torch.no_grad():
            embed = self._file_to_embed(file=file)
            inputs = self.processor(text=text, return_tensors="pt")
            speech = self.model.generate_speech(inputs["input_ids"], embed, vocoder=self.vocoder)
            return speech.numpy()
        

if __name__ == "__main__":
    import soundfile as sf

    vm = VoiceMatica()
    
    speech = vm("Hello, my dog is cute", "prompts/762583084.ogg")
    sf.write("outputs/762583084.wav", speech, 16000)
    
    # speech = vm("Hello, my dog is cute", "prompts/test.wav")
    # sf.write("outputs/test_out.wav", speech, 16000)
    
    # speech = vm("Hello, my dog is cute", "prompts/male.pt")
    # sf.write("outputs/test_man_out.wav", speech, 16000)
    
    # speech = vm("Hello, my dog is cute", "prompts/female.pt")
    # sf.write("outputs/test_woman_out.wav", speech, 16000)