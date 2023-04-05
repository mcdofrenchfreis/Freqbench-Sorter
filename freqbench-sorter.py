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
                for freq_khz, values in freqs.items():
                    coremarks = values[0]
                    coremarks_mhz = values[1]
                    power = values[2]
                    energy = values[3]
                    ulpmark = values[4]
                    # Calculate the efficiency score based on CoreMarks/MHz and ULPMark-CM (iter/mJ)
                    efficiency = (coremarks_mhz * ulpmark) / (power / 1000)
                    if efficiency > 0:
                        freq_energy_power[freq_khz] = (energy, power, efficiency)
                if freq_energy_power:
                    # Sort frequencies based on efficiency score
                    sorted_freqs_step1 = sorted(freq_energy_power.items(), key=lambda x: x[1][2], reverse=True)
                    # Sort frequencies based on CoreMarks (iter/s), dropping the lower scores up to 4 decimal places (except for the lowest and highest frequencies)
                    freqs_to_sort_step2 = [freq_khz for freq_khz, (energy, power, efficiency) in sorted_freqs_step1 if freq_khz not in [min(freq_energy_power.keys()), max(freq_energy_power.keys())]]
                    freq_coremarks = {freq_khz: freqs[freq_khz][0] for freq_khz in freqs_to_sort_step2}
                    sorted_freqs_step2 = sorted(freq_coremarks.items(), key=lambda x: x[1], reverse=True)
                    sorted_freqs[cluster][cpu] = [freq_khz for freq_khz, coremarks in sorted_freqs_step2]
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