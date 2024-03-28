import os
import subprocess
import torchaudio

PHONEME_JK = '[.w[]|{word: (.t | ascii_upcase | sub("<S>"; "sil") | sub("<SIL>"; "sil") | sub("\\(2\\)"; "") | sub("\\(3\\)"; "") | sub("\\(4\\)"; "") | sub("\\[SPEECH\\]"; "SIL") | sub("\\[NOISE\\]"; "SIL")), phones: [.w[]|{ph: .t | sub("\\+SPN\\+"; "SIL") | sub("\\+NSN\\+"; "SIL"), bg: (.b*100)|floor, ed: (.b*100+.d*100)|floor}]}]'
# pocketsphinx -phone_align yes single /content/audio.wav "Can you give me cup of tea please" \
    #     | jq '[.w[]|{word: (.t | ascii_upcase | sub("<S>"; "sil") | sub("<SIL>"; "sil") | sub("\\(2\\)"; "") | sub("\\(3\\)"; "") | sub("\\(4\\)"; "") | sub("\\[SPEECH\\]"; "SIL") | sub("\\[NOISE\\]"; "SIL")), phones: [.w[]|{ph: .t | sub("\\+SPN\\+"; "SIL") | sub("\\+NSN\\+"; "SIL"), bg: (.b*100)|floor, ed: (.b*100+.d*100)|floor}]}]' > /content/test.json

def convert_audio_to_16k(input_path: str) -> str:
    output_path = input_path[:-4] + "_16k.wav"

    waveform, sample_rate = torchaudio.load(input_path, backend="sox")
    torchaudio.save(output_path, waveform, 16000, encoding="PCM_S", bits_per_sample=16)

    return output_path

def create_phoneme(audio_path: str, text: str) -> str:
    output_path = audio_path[:-4] + "_phoneme.json"

    response= subprocess.call(
        [
            "pocketsphinx", "-phone_align", "yes", "single", "/app/"+audio_path, text,
            "|", "jq", PHONEME_JK, ">", "/app/"+output_path,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        shell=True,
        cwd="/app",
    )

    print("create phoneme code: ", response)

    return output_path

def make_video(img_path: str, audio_path, phoneme_path: str) -> str:
    output_dir = "data"

    response= subprocess.call(
        ["python3", "-m", "test_script.py", "--img_path", img_path, "--audio_path", audio_path, "--phoneme_path", phoneme_path, "--save_dir", output_dir], 
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        shell=True,
        cwd="/app/one_shot_talking_face",
    )

    print("make video code: ", response)

    output_path = output_dir + "/" + os.path.basename(img_path)[:-4] + "_" + os.path.basename(audio_path)[:-4] + ".mp4"

    return output_path