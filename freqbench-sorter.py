import csv

def read_freqbench_results(filename, little_cpus, big_cpus):
    freq_cpus = {"LITTLE": {}, "BIG": {}}
    for cpu in range(little_cpus):
        freq_cpus["LITTLE"][f"CPU {cpu}"] = {}
    for cpu in range(big_cpus):
        freq_cpus["BIG"][f"CPU {cpu}"] = {}
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cpu = int(row['CPU'])
            freq_khz = int(row['Frequency (kHz)'])
            coremarks = float(row['CoreMarks (iter/s)'])
            coremarks_mhz = float(row['CoreMarks/MHz'])
            power = float(row['Power (mW)'])
            energy = float(row['Energy (J)'])
            ulpmark = float(row['ULPMark-CM (iter/mJ)'])
            if cpu < little_cpus:
                cluster = "LITTLE"
                cpu_name = f"CPU {cpu+1}"
            else:
                cluster = "BIG"
                cpu_name = f"CPU {cpu - little_cpus+1}"
            if energy < ulpmark:
                if freq_khz not in freq_cpus[cluster][cpu_name]:
                    freq_cpus[cluster][cpu_name][freq_khz] = (coremarks, coremarks_mhz, power, energy, ulpmark)

    # Sort the frequencies in ascending order
    for cluster in freq_cpus:
        for cpu in freq_cpus[cluster]:
            freq_cpus[cluster][cpu] = dict(sorted(freq_cpus[cluster][cpu].items()))

    return freq_cpus

def get_sorted_frequencies(freq_cpus):
    sorted_freqs = {"LITTLE": {}, "BIG": {}}
    for cluster in freq_cpus:
        for cpu in freq_cpus[cluster]:
            sorted_freqs[cluster][cpu] = []
            freq_energy_power = {}
            freqs = freq_cpus[cluster][cpu]
            if freqs:
                # Step 1: Sort frequencies based on Energy (J) < ULPMark-CM (iter/mJ) and CoreMarks (iter/s)
                for freq_khz, values in freqs.items():
                    coremarks = values[0]
                    coremarks_mhz = values[1]
                    power = values[2]
                    energy = values[3]
                    ulpmark = values[4]
                    if energy < ulpmark:
                        freq_energy_power[freq_khz] = (energy, power, coremarks)

                if freq_energy_power:
                    # Step 2: Sort frequencies based on CoreMarks (iter/s) and Power (mW)
                    sorted_freqs[cluster][cpu] = sorted(freq_energy_power.keys(), key=lambda x: (freq_energy_power[x][0], freq_energy_power[x][1]), reverse=True)

                    # Filter out frequencies with lower CoreMarks scores, keeping the lowest and highest frequencies untouched
                    lowest_freq = sorted_freqs[cluster][cpu][0]
                    highest_freq = sorted_freqs[cluster][cpu][-1]
                    filtered_freqs = [freq for freq in sorted_freqs[cluster][cpu][1:-1] if round(freqs[freq][0], 4) > round(freqs[highest_freq][0], 4) or freq == highest_freq]
                    sorted_freqs[cluster][cpu] = [lowest_freq] + filtered_freqs + [highest_freq]
    return sorted_freqs
    
def main():
    filename = input("Enter the name of the freqbench results file (in CSV format): ")
    little_cpus = int(input("Enter the number of CPUs in the LITTLE cluster: "))
    big_cpus = int(input("Enter the number of CPUs in the BIG cluster: "))
    freq_cpus = read_freqbench_results(filename, little_cpus, big_cpus)
    sorted_freqs = get_sorted_frequencies(freq_cpus)
    
    # Sort the frequencies in ascending order
    for cluster in sorted_freqs:
        for cpu in sorted_freqs[cluster]:
            sorted_freqs[cluster][cpu].sort()

    print("Cluster\tFrequency (kHz)")
    for cluster in sorted_freqs:
        for cpu in sorted_freqs[cluster]:
            for freq_khz in sorted_freqs[cluster][cpu]:
                if cluster == "LITTLE":
                    cpu_type = "LITTLE"
                    cpu_num = int(cpu.split(" ")[1])
                else:
                    cpu_type = "BIG"
                    cpu_num = int(cpu.split(" ")[1]) + little_cpus
                print(f"{cpu_type}\t{freq_khz}")

if __name__ == "__main__":
    main()