"""
 Title:         Crystal/Visco Plasticity model with anisotropic hardening and latent hardening
 Description:   For creating the material file
 Author:        Janzen Choi

"""

# Libraries
from moose_sim.materials.__material__ import __Material__
from moose_sim.helper.general import flatten

# Format for defining materials
MATERIAL_FORMAT = """
<materials>
  <{material} type="SingleCrystalModel">
    <kinematics type="StandardKinematicModel">
      <emodel type="CubicLinearElasticModel">
        <m1>{c_11}</m1>
        <m2>{c_12}</m2>
        <m3>{c_44}</m3>
        <method>components</method>
      </emodel>
      <imodel type="AsaroInelasticity">
        <rule type="PowerLawSlipRule">
          <resistance type="GeneralLinearHardening">
            <M type="SquareMatrix">
              <m>12</m>
              <type>dense</type>
              <data>{glh_dense}</data>
            </M>
            <tau_0>{cp_tau_0}</tau_0>
            <absval>true</absval>
          </resistance>
          <gamma0>{cp_gamma_0}</gamma0>
          <n>{cp_n}</n>
        </rule>
      </imodel>
    </kinematics>
    <lattice type="CubicLattice">
      <a>1.0</a>
      <slip_systems>{slip_dir} ; {slip_plane}</slip_systems>
    </lattice>
    <alpha type="ConstantInterpolate">
      <v>0</v>
    </alpha>
    <update_rotation>true</update_rotation>
    <rtol>1e-08</rtol>
    <atol>1e-06</atol>
    <miter>{miter}</miter>
    <verbose>false</verbose>
    <linesearch>false</linesearch>
    <max_divide>{max_divide}</max_divide>
    <postprocessors/>
    <elastic_predictor>false</elastic_predictor>
    <fallback_elastic_predictor>true</fallback_elastic_predictor>
    <force_divide>0</force_divide>
    <elastic_predictor_first_step>false</elastic_predictor_first_step>
  </{material}>
</materials>
"""

# VSHAI Class
class Material(__Material__):
    
    def get_material(self, c_11:float, c_12:float, c_44:float) -> str:
        """
        Gets the content for the material file;
        must be overridden

        Parameters:
        * `c_11`:     The component of the elastic tensor in (0,0)
        * `c_12`:     The component of the elastic tensor in (0,1)
        * `c_44`:     The component of the elastic tensor in (3,3)
        """
        
        # Define information about the material
        slip_systems = 12
        
        # Define hardening matrix
        cp_lh = [self.get_param(f"cp_lh_{i}") for i in range(6)]
        sm_data = get_big_lh_matrix(cp_lh)
        glh_dense = " ".join([str(sm) for sm in flatten(sm_data)])
            
        # Define tau_0 values
        cp_tau_0 = self.get_param("cp_tau_0")
        cp_tau_0 = " ".join([str(cp_tau_0)]*slip_systems)
        
        # Define material content
        material_content = MATERIAL_FORMAT.format(
            material   = self.get_name(),
            c_11       = c_11,
            c_12       = c_12,
            c_44       = c_44,
            glh_dense  = glh_dense,
            cp_tau_0   = cp_tau_0,
            cp_gamma_0 = self.get_param("cp_gamma_0"),
            cp_n       = self.get_param("cp_n"),
            slip_dir   = "1 1 0",
            slip_plane = "1 1 1",
            miter      = 50,
            max_divide = 4,
        )
        return material_content

def get_big_lh_matrix(params:tuple) -> list:
    """
    Gets the 12x12 latent hardening matrix
    
    Parameters:
    * `params`: Elements of the matrix
    
    Returns the matrix in the form of a list of lists
    """
    h_0, h_1, h_2, h_3, h_4, h_5 = params
    lh_matrix = [
        [h_0, h_1, h_1, h_3, h_4, h_4, h_2, h_4, h_5, h_2, h_5, h_4],
        [h_1, h_0, h_1, h_4, h_2, h_5, h_4, h_3, h_4, h_5, h_2, h_4],
        [h_1, h_1, h_0, h_4, h_5, h_2, h_5, h_4, h_2, h_4, h_4, h_3],
        [h_3, h_4, h_4, h_0, h_1, h_1, h_2, h_5, h_4, h_2, h_4, h_5],
        [h_4, h_2, h_5, h_1, h_0, h_1, h_5, h_2, h_4, h_4, h_3, h_4],
        [h_4, h_5, h_2, h_1, h_1, h_0, h_4, h_4, h_3, h_5, h_4, h_2],
        [h_2, h_4, h_5, h_2, h_5, h_4, h_0, h_1, h_1, h_3, h_4, h_4],
        [h_4, h_3, h_4, h_5, h_2, h_4, h_1, h_0, h_1, h_4, h_2, h_5],
        [h_5, h_4, h_2, h_4, h_4, h_3, h_1, h_1, h_0, h_4, h_5, h_2],
        [h_2, h_5, h_4, h_2, h_4, h_5, h_3, h_4, h_4, h_0, h_1, h_1],
        [h_5, h_2, h_4, h_4, h_3, h_4, h_4, h_2, h_5, h_1, h_0, h_1],
        [h_4, h_4, h_3, h_5, h_4, h_2, h_4, h_5, h_2, h_1, h_1, h_0]
    ]
    return lh_matrix
