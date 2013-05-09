f = open("output.txt","r")

retinas = []

while True:
    line = f.readline()
    if line == "": break

    if line[0] == "~":
        f.readline()
        
        retina_name = f.readline().rstrip()
        
        f.readline()
        width = f.readline().rstrip().split("\t")[-1]
        grid_size = f.readline().rstrip().split("\t")[-1]
        timestep = f.readline().rstrip().split("\t")[-1]
        cone_distance = f.readline().rstrip().split("\t")[-1]
        cone_density = f.readline().rstrip().split("\t")[-1]
        cone_input_size = f.readline().rstrip().split("\t")[-1]
        input_strength = f.readline().rstrip().split("\t")[-1]
        decay = f.readline().rstrip().split("\t")[-1]
        diffusion = f.readline().rstrip().split("\t")[-1]
        bipolar_distance = f.readline().rstrip().split("\t")[-1]
        bipolar_density = f.readline().rstrip().split("\t")[-1]
        bipolar_input = f.readline().rstrip().split("\t")[-1]
        
        
        retina_info = [retina_name, width, grid_size, timestep,
                       cone_distance, cone_density, cone_input_size,
                       input_strength, decay, diffusion,
                       bipolar_distance, bipolar_density, bipolar_input]
                       
        bipolar_sum = [0.0, 0.0]
        
        for stim in range(26):
            for x in range(11):
                f.readline()
            bipolar_bounds = f.readline().rstrip().split("\t")[-1]
            bipolar_bounds = eval(bipolar_bounds)
            bipolar_sum[0] += bipolar_bounds[0]
            bipolar_sum[1] += bipolar_bounds[1]
            f.readline()
        
        bipolar_sum[0]/=26
        bipolar_sum[1]/=26
        
        
        retinas.append([retina_info, bipolar_sum])
        
        
        
        
f.close()
for r in retinas: 
    print r[0]
    print r[1]
    print