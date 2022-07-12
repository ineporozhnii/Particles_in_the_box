import numpy as np
import matplotlib
import matplotlib.pyplot as plt


class Particles():
    """
    This class holds particles' positions, velocities, accelerations, and properties
    """
    def __init__(self, x, y, v_x, v_y, a_x, a_y, radii, vector_of_masses) -> None:
        self.radii = radii
        self.mass = vector_of_masses
        self.colors = "cornflowerblue"
        self.x = x
        self.y = y
        self.v_x = v_x
        self.v_y = v_y
        self.a_x = a_x
        self.a_y = a_y
        self.radii_sum = self.radii[:, None] + self.radii[None, :]


def get_init_conditions(n_particles, position_limits_x, position_limits_y, velocity_limits_x, velocity_limits_y, radii_limits):
    """
    This function creates initial distribution of particle positions, velocities, and radii
    Input:
        n_atoms - number of atoms in the simulations
        position_limits_x - list of low and high limits for initial atomic positions on x axis
        position_limits_y - list of low and high limits for initial atomic positions on y axis
        velocity_limits_x - list of low and high limits for initial atomic velocities on x axis
        velocity_limits_y - list of low and high limits for initial atomic velocities on y axis
    Output:
        x_init - initial x coordinates 
        y_init - initial y coordinates 
        v_x_init - initial x velocities 
        v_y_init - initial y velocities 
        radii - vector of particles' radii 
    """
    radii = np.random.uniform(low=radii_limits[0], high=radii_limits[1], size=(n_particles,))
    coordinates = []
    x_first = np.random.uniform(low=position_limits_x[0], high=position_limits_x[1], size=(1,))[0]
    y_first = np.random.uniform(low=position_limits_y[0], high=position_limits_y[1], size=(1,))[0]
    coordinates.append([x_first, y_first])
    print(x_first)
    while len(coordinates) < n_particles: 
        x_check = np.random.uniform(low=position_limits_x[0], high=position_limits_x[1], size=(1,))[0]
        y_check = np.random.uniform(low=position_limits_y[0], high=position_limits_y[1], size=(1,))[0]
        coordinates.append([x_check, y_check])
        radii_sum = radii[:len(coordinates), None] + radii[None, :len(coordinates)]
        distance_matrix = np.linalg.norm(np.array(coordinates) - np.array(coordinates)[:,None], axis=-1)
        print(distance_matrix)
        overlapping_particles_indicies = np.where((distance_matrix != 0) & (distance_matrix <= radii_sum+1.0))
        if overlapping_particles_indicies[0].shape[0] > 0:
            del coordinates[-1]
             
    x_init = np.array(coordinates).T[0]
    y_init = np.array(coordinates).T[1]

    v_x_init = np.random.uniform(low=velocity_limits_x[0], high=velocity_limits_x[1], size=(n_particles,))
    v_y_init = np.random.uniform(low=velocity_limits_y[0], high=velocity_limits_y[1], size=(n_particles,))
    return x_init, y_init, v_x_init, v_y_init, radii


def translate(particles, dt=0.01):
    x_new = particles.x + particles.v_x * dt
    y_new = particles.y + particles.v_y * dt
    return x_new, y_new


def accelerate(particles, dt=0.01):
    particles.v_x = particles.v_x + particles.a_x * dt
    particles.v_y = particles.v_y + particles.a_y * dt


def update_positions(particles, x_new, y_new, box_size_x, box_size_y, restitution_coef_bc=1.0):
    # Box boundary collisions
    particles.v_x[np.where(x_new + particles.radii > box_size_x/2)] = -1 * restitution_coef_bc * particles.v_x[np.where(x_new + particles.radii > box_size_x/2)]
    particles.v_x[np.where(x_new - particles.radii < -box_size_x/2)] = -1 * restitution_coef_bc * particles.v_x[np.where(x_new - particles.radii < -box_size_x/2)]
    particles.v_y[np.where(y_new + particles.radii > box_size_y/2)] = -1 * restitution_coef_bc * particles.v_y[np.where(y_new + particles.radii > box_size_y/2)]
    particles.v_y[np.where(y_new - particles.radii < -box_size_y/2)] = -1 * restitution_coef_bc * particles.v_y[np.where(y_new - particles.radii < -box_size_y/2)]
    x_new[np.where(x_new + particles.radii > box_size_x/2)] = box_size_x/2 - particles.radii[np.where(x_new + particles.radii > box_size_x/2)]
    x_new[np.where(x_new - particles.radii < -box_size_x/2)] = -box_size_x/2 + particles.radii[np.where(x_new - particles.radii < -box_size_x/2)]
    y_new[np.where(y_new + particles.radii > box_size_y/2)] = box_size_y/2 - particles.radii[np.where(y_new + particles.radii > box_size_y/2)]
    y_new[np.where(y_new - particles.radii < -box_size_y/2)] = -box_size_y/2 + particles.radii[np.where(y_new - particles.radii < -box_size_y/2)]
    # Update particle positions
    particles.x = x_new
    particles.y = y_new


def calculate_distances(particles):
    coordinates = np.column_stack((particles.x, particles.y))
    distance_matrix = np.linalg.norm(coordinates - coordinates[:,None], axis=-1)
    return distance_matrix

def get_colliding_particles_unique_index_pairs(colliding_particles_indicies):
    colliding_particles_all_index_pairs = np.column_stack((colliding_particles_indicies[0], colliding_particles_indicies[1]))
    colliding_particles_unique_index_pairs = np.array(list(set(tuple(sorted(index_pair)) for index_pair in colliding_particles_all_index_pairs)))
    return colliding_particles_unique_index_pairs


def simulate(frame_idx, particles, ax, box_size_x, box_size_y, restitution_coef_bc, restitution_coef_pc):
    x_new, y_new = translate(particles)
    # Add acceleration before position update
    if frame_idx%2 != 0:
        accelerate(particles)
    update_positions(particles, x_new, y_new, box_size_x, box_size_y, restitution_coef_bc)
    # Add acceleration after position update
    if frame_idx%2 == 0:
        accelerate(particles)

    # Calculate velocities
    velocities = np.sqrt(particles.v_x**2 + particles.v_y**2)
    # Find distances between particles
    distance_matrix = calculate_distances(particles)
    # Find indicies of colliding partilces
    colliding_particles_indicies = np.where((distance_matrix != 0) & (distance_matrix < particles.radii_sum))
    if colliding_particles_indicies[0].shape[0] > 0:
        collision(particles, colliding_particles_indicies, velocities, restitution_coef_pc)
    # Plot particles
    ax.clear()
   # ax.scatter(particles.x, particles.y, s=100, c=velocities, cmap='viridis', label = f"Average velocity {np.mean(velocities)}")
    color_map = matplotlib.cm.jet
    circles = [plt.Circle((x_i, y_i), radius=r) for x_i, y_i, r, v in zip(particles.x, particles.y, particles.radii, velocities)]
    collection = matplotlib.collections.PatchCollection(circles, cmap=matplotlib.cm.jet, alpha=0.8)
    collection.set_edgecolors('b')
    collection.set_linewidth(1)
    collection.set_array(velocities)
    collection.set_clim([0, 20])
    ax.add_collection(collection)
    ax.axis('equal')
    ax.set_xlim([-box_size_x/2, box_size_x/2])
    ax.set_ylim([-box_size_y/2, box_size_y/2])
    plt.xticks([], [])
    plt.yticks([], [])
    #print(f"Average velocity {np.mean(velocities)}")


def collision(particles, colliding_particles_indicies, restitution_coef_pc=1.0, adjust_positions=True):
    """
    This function calculates and updates velocities of particles after collision
    Input: 
        particles - holds information about all particles
        colliding_particles_indicies  - indicies of particles that collide (determined from distance matrix)
        restitution_coef_pc - determines how much energy lost during particle-particle collision (=1 for elastic collisions, <1 for inelastic collisions)
        adjust_positions - if True, shifts particle positions during collision from circle overlap to circle contact to prevent particle binding

    Distance matrix is symmetric and therefore collision search provides each colliding particle pair twice (with permuted indicies)  
    We can exclude permutated indicies by taking set of sorted index pairs
    """

    colliding_particles_unique_index_pairs = get_colliding_particles_unique_index_pairs(colliding_particles_indicies)
    colliding_particles_1 = colliding_particles_unique_index_pairs.T[0]
    colliding_particles_2 = colliding_particles_unique_index_pairs.T[1]
    
    print(colliding_particles_indicies)
    print(colliding_particles_1, " ", colliding_particles_2)
    
    if adjust_positions:
        positions = np.column_stack((particles.x, particles.y))
        distances = np.linalg.norm(positions[colliding_particles_1] - positions[colliding_particles_2], axis=1)
        norm_vector = (positions[colliding_particles_1] - positions[colliding_particles_2])/distances[:, None]
        shifts = (particles.radii[colliding_particles_1] + particles.radii[colliding_particles_2] - distances)/2
        print(f"Shifts {shifts}")
        adjusted_positions_1 = positions[colliding_particles_1] + shifts[:, None] * norm_vector
        adjusted_positions_2 = positions[colliding_particles_2] - shifts[:, None] * norm_vector
        particles.x[colliding_particles_1] = adjusted_positions_1.T[0]
        particles.y[colliding_particles_1] = adjusted_positions_1.T[1]
        particles.x[colliding_particles_2] = adjusted_positions_2.T[0]
        particles.y[colliding_particles_2] = adjusted_positions_2.T[1]

    velocities = np.column_stack((particles.v_x, particles.v_y))
    positions = np.column_stack((particles.x, particles.y))
 
    impact_velocities_1 = np.sum((velocities[colliding_particles_1] - velocities[colliding_particles_2]) * (positions[colliding_particles_1] - positions[colliding_particles_2]), axis=1)
    impact_velocities_1 = (positions[colliding_particles_1] - positions[colliding_particles_2])/(np.linalg.norm(positions[colliding_particles_1] - positions[colliding_particles_2], axis=1)**2)[:, None] * impact_velocities_1[:, None]
    effective_mass_1 = (1+restitution_coef_pc) * particles.mass[colliding_particles_2]/(particles.mass[colliding_particles_1] + particles.mass[colliding_particles_2])
    delta_v_1 = effective_mass_1[:, None] * impact_velocities_1

    impact_velocities_2 = np.sum((velocities[colliding_particles_2] - velocities[colliding_particles_1]) * (positions[colliding_particles_2] - positions[colliding_particles_1]), axis=1)
    impact_velocities_2 = (positions[colliding_particles_2] - positions[colliding_particles_1])/(np.linalg.norm(positions[colliding_particles_2] - positions[colliding_particles_1], axis=1)**2)[:, None] * impact_velocities_2[:, None]
    effective_mass_2 = (1+restitution_coef_pc) * particles.mass[colliding_particles_1]/(particles.mass[colliding_particles_1] + particles.mass[colliding_particles_2])
    delta_v_2 = effective_mass_2[:, None] * impact_velocities_2

    particles.v_x[colliding_particles_1] = particles.v_x[colliding_particles_1] - delta_v_1.T[0]
    particles.v_y[colliding_particles_1] = particles.v_y[colliding_particles_1] - delta_v_1.T[1]
    particles.v_x[colliding_particles_2] = particles.v_x[colliding_particles_2] - delta_v_2.T[0]
    particles.v_y[colliding_particles_2] = particles.v_y[colliding_particles_2] - delta_v_2.T[1]
