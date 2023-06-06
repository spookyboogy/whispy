# Usage:

- " "

## Using [Colab](https://research.google.com/colaboratory/faq.html#whats-colaboratory)

- " "
- When using a standard (free) runtime, running both whisper and pyannote/speaker-diarization on long audio files can take hours (see [time and performance](#scrollTo#todo). Once you've selected your options, started your runtime, and uploaded your file, you can close the tab or leave it in the background until it finishes. However, you should take colab's [usage limits](https://research.google.com/colaboratory/faq.html#usage-limits) and [idle timeout rules](https://research.google.com/colaboratory/faq.html#idle-timeouts) into account when deciding how to use the notebooks. If you do experience a runtime interruption, you may need to [reset your runtime](https://research.google.com/colaboratory/faq.html#forced-availability).
- More about colab's [free vs subscription](https://colab.research.google.com/#scrollTo=BJW8Qi-pPpep) runtimes 
- " "

## Time and Performance considerations

<details>
<summary> graphs </summary>

![cpu_vs_gpu](resources/Whisper-cpu_vs_gpu.png "The difference in time required to run whisper on a GPU vs a CPU")
![model_size](resources/Whisper-model_size.png "The difference in time it takes to run different sized models on CPU or GPU. Notice that the large model is not included in second CPU graph because it is considered very time-inefficient in comparison to running large on GPU")
![cpu_vs_gpu_vs_model](resources/Whisper-Transcription-Performance-1.png)

</details>

<br> </br>

## Troubleshooting
<details>
<summary> short troubleshooting video </summary>

[!['vid'](https://img.youtube.com/vi/mBYmFuD8G2Y/default.jpg)](https://www.youtube.com/watch?v=mBYmFuD8G2Y)

</details>


<br> </br>
## Todo:
<details>
<summary>  </summary>

- [ ] write all the documentation and usage guide
- [ ] add more image resources, add to notebook 
- [ ] write separate notebooks for whispy, diarize, and merge

</details>