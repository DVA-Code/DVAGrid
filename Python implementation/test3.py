import ku_grid_model
network = ku_grid_model.create_network()
network.pf()
print(network.lines_t.p0)
print(network.lines_t.p1)