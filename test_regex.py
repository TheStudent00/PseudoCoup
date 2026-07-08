line = '            std::cout << "No station assigned." << std::endl;'
if "std::cout" in line:
    parts = line.split(" << ")
    args = []
    for p in parts[1:]:
        p = p.strip().strip(";")
        if p == "std::endl": continue
        args.append(p)
    res = line[:line.find("std::cout")] + "print(" + " + ".join(args) + ")"
    print("RESULT:", repr(res))
