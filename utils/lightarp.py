import time
import numpy as np

class light_arp:
    def __init__(self, dist_matrix, time_func = lambda x: x, light_func = lambda x: np.maximum( x, 0)):
        self.dist_matrix = dist_matrix # matrix n*n 
        self.light_func = light_func
        self.time_func = time_func
        self.n = self.dist_matrix.shape[0]
        self.notes_in =  [False] * self.n
        self.note_time = [0]     * self.n
        self.notes_out = [0.0]   * self.n

    def note_on(self, note):
        # accepts a note from 0 to n
        self.notes_in[note] = True
        self.note_time[note] = time.time()
    
    def note_off(self, note):
        # accepts a note from 0 to n
        self.notes_in[note] = False

    def get_light_levels(self):
        out_mat = np.zeros((self.n, self.n))

        for note in range(self.n):
            note_time_mod =  self.time_func( (time.time() - self.note_time[note]) )
            out_mat[note, :] = self.light_func (note_time_mod - self.dist_matrix[note, :]) * self.notes_in[note]
        out_mat = np.minimum( np.sum(out_mat, axis = 0) , 1)
        return(out_mat)

if __name__ == "__main__":
    np.set_printoptions(1)
    n = 11
    a = np.tile(np.arange(n),(n,1))
    dist_mat = np.abs(a - a.transpose())
    la = light_arp(dist_mat, lambda x: np.log(20*x+1), lambda x: np.maximum( x*(2-x),0))
    la.note_on(5)


    for i in range(0,50): 
        print(la.get_light_levels())
        time.sleep(0.1)
        
    la.note_off(5)
    for i in range(0,10):
        print(la.get_light_levels())
        time.sleep(0.1)

    