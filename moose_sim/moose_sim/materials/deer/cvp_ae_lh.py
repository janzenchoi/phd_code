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
  <{material}_cp type="SingleCrystalModel">
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
  </{material}_cp>
  <{material}_vp type="GeneralIntegrator">
		<elastic type="IsotropicLinearElasticModel">
      <m1_type>youngs</m1_type>
      <m1>{youngs}</m1>
      <m2_type>poissons</m2_type>
      <m2>{poissons}</m2>
		</elastic>
		<rule type="TVPFlowRule">
			<elastic type="IsotropicLinearElasticModel">
        <m1_type>youngs</m1_type>
        <m1>{youngs}</m1>
        <m2_type>poissons</m2_type>
        <m2>{poissons}</m2>
			</elastic>
			<flow type="PerzynaFlowRule">
				<surface type="IsoJ2"/>
				<hardening type="VoceIsotropicHardeningRule">
					<s0>{vp_s0}</s0>
					<R>{vp_R}</R>
					<d>{vp_d}</d>
				</hardening>
				<g type="GPowerLaw">
					<n>{vp_n}</n>
					<eta>{vp_eta}</eta>
				</g>
			</flow>
		</rule>
		<alpha type="ConstantInterpolate">
			<v>0</v>
		</alpha>
		<truesdell>false</truesdell>
		<rtol>1e-08</rtol>
		<atol>1e-08</atol>
		<miter>{miter}</miter>
		<verbose>false</verbose>
		<linesearch>false</linesearch>
		<max_divide>{max_divide}</max_divide>
		<force_divide>false</force_divide>
		<skip_first_step>false</skip_first_step>
  </{material}_vp>
</materials>
"""

# VSHAI Class
class Material(__Material__):
    
    def get_material(self, c_11:float, c_12:float, c_44:float, youngs:float,
                     poissons:float) -> str:
        """
        Gets the content for the material file;
        must be overridden

        Parameters:
        * `c_11`:     The component of the elastic tensor in (0,0)
        * `c_12`:     The component of the elastic tensor in (0,1)
        * `c_44`:     The component of the elastic tensor in (3,3)
        * `youngs`:   The elastic modulus
        * `poissons`: The poisson ratio
        """
        
        # Define information about the material
        slip_systems = 12
        
        # Define hardening matrix
        cp_lh_0 = self.get_param("cp_lh_0")
        cp_lh_1 = self.get_param("cp_lh_1")
        sm_data = [[cp_lh_0]*slip_systems for _ in range(slip_systems)]
        for i in range(slip_systems):
            sm_data[i][i] = cp_lh_1
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
            youngs     = youngs,
            poissons   = poissons,
            glh_dense  = glh_dense,
            cp_tau_0   = cp_tau_0,
            cp_gamma_0 = self.get_param("cp_gamma_0"),
            cp_n       = self.get_param("cp_n"),
            vp_s0      = self.get_param("vp_s0"),
            vp_R       = self.get_param("vp_R"),
            vp_d       = self.get_param("vp_d"),
            vp_n       = self.get_param("vp_n"),
            vp_eta     = self.get_param("vp_eta"),
            slip_dir   = "1 1 0",
            slip_plane = "1 1 1",
            miter      = 50,
            max_divide = 4,
        )
        return material_content
    