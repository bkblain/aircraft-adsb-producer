#!/usr/bin/env python
"""
Run this file when a plane is near to capture a single set of samples.
"""

import time

import adsb_rtlsdr
import numpy as np
import pyModeS as pms

# example raw message
# 8D4840D6202CC371C32CE0576098
# pms.tell("8D4840D6202CC371C32CE0576098")


sample_rate = 2e6
samples_per_microsec = 200
center_freq = 1090e6
signal_buffer = []
messages = []

# All Mode S replies start with an 8 μs fixed preamble and continue with 56- or 112 μs data block.

pbits = 8
fbits = 112
message_length = pbits * 2 + (fbits + 1) * 2
preamble = [1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0]


th_amp_diff = 0.8  # signal amplitude threshold difference between 0 and 1 bit


# capture1 = 200001122AB752
samples = np.loadtxt("target/capture1.txt", delimiter=',', dtype=np.complex128)

print(samples[0])
print(len(samples))


# removing "negative frequencies" (based on numpy, I think this makes it scalar
# - remember 'j' is imaginary number)
# original complex128 type = (-0.0039215686274509665-0.0039215686274509665j)
# resulting signal_buffer = 0.005545935538718
#
# https://pysdr.org/content/frequency_domain.html
# https://numpy.org/doc/stable/reference/generated/numpy.absolute.html

amp = np.absolute(samples)
signal_buffer.extend(amp.tolist())

print(signal_buffer[0])
print(len(signal_buffer))

# To see what the resulting plot looks like, uncomment these lines
# -----------------------------------------------------------------------------
adsb_rtlsdr.AdsbRtlSdr.plot_psd(signal_buffer, sample_rate, center_freq)
# -----------------------------------------------------------------------------

# minimum calculated noise or default to 1 microsecond
noise_floor = min(adsb_rtlsdr.AdsbRtlSdr.calculate_noise_floor(
    signal_buffer, sample_rate), 1e6)

# set minimum signal amplitude
# 10 dB SNR
# SNR = Signal to Noise Ratio = 3.162
#
# I don't understand why they are using a constant instead of calculating the value
#
# https://www.electronics-tutorials.ws/filter/decibels.html
# https://dsp.stackexchange.com/questions/70779/how-is-signal-to-noise-ratio-actually-measured-by-receiver-equipment
# https://documentation.meraki.com/MR/WiFi_Basics_and_Best_Practices/Signal-to-Noise_Ratio_(SNR)_and_Wireless_Signal_Strength
min_sig_amp = 3.162 * noise_floor

buffer_length = len(signal_buffer)

i = 0

while i < (buffer_length - message_length):

    # Anything that is below the minimum signal amplitude can be skipped
    if signal_buffer[i] >= min_sig_amp:

        # The pulses are about 0.8 μs wide. P1 and P3 are the two main pulses sent by
        # the directional antenna. They are separated by 8 μs and 21 μs, respectively
        # for Mode A and C. P2 is a pulse emitted through the omnidirectional antenna
        # right after P1. Pulse P2 is introduced for sidelobe suppression
        # [Orlando 1989]. When the power of P2 is higher than P1, the interrogation
        # is likely from the side lobes of the directional antenna and should be
        # ignored by the aircraft. This is can happen when the aircraft is close to
        # the radar.
        # https://mode-s.org/decode/content/introduction.html

        check = True
        pulses = signal_buffer[i: i + pbits * 2]

        # I guess this checks to make sure it's not at the end of the array
        # if len(pulses) != 16:
        #     check = False
        # else:

        for k in range(16):
            # th_amp_diff = signal amplitude threshold difference between 0 and 1 bit
            if abs(pulses[k] - preamble[k]) > th_amp_diff:
                check = False
                break

        if check:
            print('current i =' + str(i))

            frame_start = i + pbits * 2
            frame_end = i + pbits * 2 + (fbits + 1) * 2
            frame_length = (fbits + 1) * 2
            frame_pulses = signal_buffer[frame_start:frame_end]

            print('frame start = ' + str(frame_start))
            print('frame end = ' + str(frame_end))
            print('')

            adsb_rtlsdr.AdsbRtlSdr.plot(frame_pulses)

            threshold = max(frame_pulses) * 0.2

            msgbin = []
            for j in range(0, frame_length, 2):
                p2 = frame_pulses[j: j + 2]
                if len(p2) < 2:
                    break

                if p2[0] < threshold and p2[1] < threshold:
                    break
                elif p2[0] >= p2[1]:
                    c = 1
                elif p2[0] < p2[1]:
                    c = 0
                else:
                    msgbin = []
                    break

                msgbin.append(c)

            # why is the first data 56 but the second data len 57?
            # I think there is an off by 1 bug in here (df=4 and df=8).
            # the df=8 indicates there needs to be another 0 in front of the binary string

            print('msgbin ' + str(len(msgbin)))
            print(msgbin)

            # advance i with a jump
            i = frame_start + j

            if len(msgbin) > 0:
                msg = pms.bin2hex("".join([str(i) for i in msgbin]))
                print('msg = ' + msg)

                # df = downlink format
                # Mode-S ADS-B technology has two types of squitter, a short, 56 bit, acquisition
                # squitter which can contain Downlink Formats (DF) 0, 4, 5 and 11 (DF0/4/5/11)
                # and the 112 bit extended squitter (ES) which can contain DF17.
                # https://cdn.knmi.nl/knmi/pdf/bibliotheek/knmipubTR/TR336.pdf

                df = pms.df(msg)
                print('df = ' + str(df))
                msglen = len(msg)
                checkMsg = False

                if df == 17 and msglen == 28:
                    if pms.crc(msg) == 0:
                        checkMsg = True
                elif df in [20, 21] and msglen == 28:
                    checkMsg = True
                elif df in [4, 5, 11] and msglen == 14:
                    checkMsg = True

                if checkMsg:
                    messages.append([msg, time.time()])

                # if self.debug:
                #     self._debug_msg(msghex)

    # elif i > buffer_length - 500:
    #     # save some for next process
    #     break
    # else:
    #     i += 1

    i += 1


print('i = ' + str(i))

# reset the buffer
signal_buffer = signal_buffer[i:]

print(messages)
pms.tell(messages[0][0])
