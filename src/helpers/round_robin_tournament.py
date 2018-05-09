def schedule(teams):
    if len(teams) % 2:
        sys.exit('Number of teams must be even: add a fake team for odd teams')

    rotation = list(teams) # copy the list

    rotation_list = []
    for i in range(0, len(teams) - 1):
        rotation_list.append(rotation)
        rotation = [rotation[0]] + [rotation[-1]] + rotation[1:-1]

    ret = []
    for r in rotation_list:
        ret.append(zip(*[iter(r)]*2))

    return ret
