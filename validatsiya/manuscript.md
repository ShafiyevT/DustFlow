::: {custom-style="TSP Title"}
A Coupled Three-Dimensional Model of Dust Emission and Transport under Wind Erosion Accounting for the Physical and Mechanical Properties of Particles
:::

::: {custom-style="TSP Authors"}
Madina Bobojonova^1,\*^, Tursun Shafiyev^1^ and Normakhmad Ravshanov^2^
:::

::: {custom-style="TSP Affiliation"}
^1^Department of Artificial Intelligence and Information Security, Bukhara State University, Bukhara, 200117, Uzbekistan

^2^Scientific and Innovation Center of Information and Communication Technologies, Tashkent, 100125, Uzbekistan

\*Corresponding Author: Madina Bobojonova. Email: [to be provided]

Received: XX Month Year; Accepted: XX Month Year; Published: XX Month Year
:::

::: {custom-style="TSP Abstract"}
**ABSTRACT:** Wind erosion and the resulting atmospheric dust loading are among the main environmental problems of the arid territories of Central Asia. The process consists of two stages, the detachment of particles from the soil surface and their subsequent transport by the air flow, which most existing models treat separately: the emission flux is computed by a stand-alone scheme and inserted into the transport equation as a volume source in the lowest model layer. This paper presents a three-dimensional non-stationary model in which both stages form a single boundary-value problem. The vertical dust flux, computed by a two-step saltation–sandblasting scheme, enters the formulation as a boundary condition of the third kind at the underlying surface, where it is balanced by dry deposition; the direction of the net surface exchange then follows from the sign of the difference between emission and deposition, and the transition between the two regimes is continuous. The dust is resolved into transport fractions whose gravitational settling velocities differ by more than four orders of magnitude. All surface-state factors (soil moisture, clay content, roughness elements and aerodynamic roughness) are combined into a single effective threshold friction velocity, and the terrain is represented by a terrain-following coordinate. The transport equation is written in a generalized form in which advection is performed with the actual particle velocity obtained from the particle relaxation equations; the classical form with the air velocity and a separate settling term is recovered as a limiting case, and quantitative bounds of its applicability are given. The integral mass budget, the non-negativity of the solution, the continuity of the regime transition, limiting cases and the governing dimensionless numbers are established analytically. A 48-hour simulation of the dust storm of 28–29 April 2025 over the Bukhara region (Uzbekistan), driven by reanalysis meteorology and global soil and land-cover data, shows that replacing the five transport fractions by a single effective mode underestimates dry deposition by a factor of 5.1 and overestimates the near-surface concentration by 21% on average and by up to 38% over one tenth of the domain. Compared with ground-based observations, the fraction-resolved model reproduces the PM~2.5~/PM~10~ ratio of storm dust (0.13 vs. an observed 0.13–0.21), whereas the operational Copernicus Atmosphere Monitoring Service (CAMS) reanalysis gives 0.48.
:::

::: {custom-style="TSP Keywords"}
**KEYWORDS:** Wind erosion; dust emission; advection–diffusion equation; boundary condition of the third kind; size-resolved transport; settling velocity; mathematical modelling; Central Asia
:::

# Introduction

Arid and semi-arid lands cover more than one third of the continental surface and are the main source of mineral aerosol in the atmosphere [1–3]. Wind erosion removes the finest and most fertile soil fraction, and the entrained dust is transported over hundreds to thousands of kilometres, altering the radiation balance, degrading air quality and depositing far from the source. In Central Asia the problem has been aggravated by the desiccation of the Aral Sea: the exposed seabed, the Aralkum, has become a significant anthropogenic dust source that adds about 7% per year to the total dust amount over the region [4], and dust storms are recorded at meteorological stations across Uzbekistan on up to several tens of days per year, with more than 30 days per year in the Bukhara region [5–7].

Several practical tasks require quantitative forecasts of dust concentration fields. Public health services need forecasts of exceedances of air-quality limits for the PM~10~ and PM~2.5~ fractions at least one day ahead. Agriculture needs estimates of topsoil loss from specific fields in order to plan shelterbelts and tillage practices, which cannot be measured over entire territories. Planning of sand fixation and phytomelioration projects requires scenario calculations of how emission changes when particular areas are stabilized. Infrastructure operators need estimates of visibility and dust loading for roads, airports and solar power plants. In all these cases in situ measurements provide values at individual points and times, whereas decisions require the concentration field over the whole territory and its evolution; the only tool that provides such a picture is mathematical modelling.

Physically the process consists of two stages. First, particles are detached from the soil surface and lifted into the surface layer; the controlling factors are the threshold friction velocity, soil moisture, particle size distribution, roughness elements and aerodynamic roughness. Second, the lifted particles are carried by the air flow and dispersed by turbulent diffusion, and the result is controlled by the turbulence regime of the boundary layer, gravitational settling and orography.

Existing models describe both stages but, as shown in Section 2, usually separately: the emission flux is computed by a dedicated scheme and passed to the transport model as a prescribed volume source. In addition, the particle size distribution is either reduced to a single effective mode or represented by fractions with fixed settling velocities, although both the settling velocity and the horizontal particle velocity components are formed by the wind field and vary with it.

This work addresses these points. Its contributions are as follows:

1. Emission and transport are combined into one boundary-value problem: the detachment flux enters as a boundary condition of the third kind at the underlying surface, where it is balanced by dry deposition. The same boundary relation describes emission and deposition, so that the transition between the two regimes is continuous and requires no switching between models, and no injection layer has to be chosen for the emission flux.
2. The emission is resolved into transport fractions, each with its own settling velocity and dry-deposition velocity. All surface-state factors are combined into a single effective threshold velocity, which makes the model configurable from available soil maps and remote sensing data and simplifies sensitivity analysis.
3. The transport equation is written in a generalized form in which advection is performed with the actual particle velocity obtained from the particle relaxation equations. The classical form is a limiting case, and the particle sizes and distances for which it is sufficient are established quantitatively. This result is methodological: it delimits the range of applicability of the classical form rather than replacing it.
4. The properties of the model are established analytically: the integral mass budget, the non-negativity of the solution, the continuity of the regime transition, limiting cases and dimensionless numbers that determine the transport regime.

The paper is organized as follows. Section 2 reviews the state of research. Section 3 formulates the problem and the assumptions. Section 4 derives the model, Section 5 presents the parameterizations, and Section 6 establishes the properties of the model. Section 7 outlines the numerical implementation, Section 8 presents a computational experiment for a real dust storm, Section 9 discusses the limitations, and Section 10 concludes.

# State of Research

**Physics of particle entrainment.** The quantitative description of wind erosion goes back to the experiments of Bagnold [8], who identified saltation as the main transport mechanism of sand and related the horizontal saltation flux to the cube of the friction velocity. Owen [9] explained the self-regulation of the saltation layer through the change of effective roughness; similar expressions for the horizontal flux were obtained by Kawamura [10] and White [11], and early systematic experiments were performed by Chepil [12]. Later work moved from the horizontal saltation flux to the vertical flux of fine dust, which determines atmospheric dust loading. Two lines of research emerged. The first relates the vertical flux to the horizontal flux through an empirical efficiency coefficient that depends on the clay content [13,14]. The second is based on the bombardment of the surface by saltating grains, with explicit description of the ejection and disaggregation of soil aggregates [15–18]. The second line is physically more consistent, as confirmed later [19–21], but requires data on aggregate binding energies that are rarely available for a specific territory. The present work adopts the first approach, complemented by size resolution of the emitted dust.

**Threshold and surface state.** The dependence of the threshold friction velocity on particle diameter, with a minimum in the range of about 75–100 µm, was established experimentally [22] and received a compact analytical expression [23]: for smaller particles the threshold increases because of interparticle cohesion, for larger ones because of weight. The effect of soil moisture is described by the correction of Fécan et al. [24], which accounts for capillary bridges between grains and acts only above a residual moisture that itself depends on the clay content. The effect of vegetation and non-erodible roughness elements is introduced through the drag-partition scheme of Raupach et al. [25], and field estimates of threshold friction velocity for arid lands are systematized in [26]. The size distribution of erodible soils is represented by a sum of lognormal modes [27]. These three corrections were developed independently, and the legitimacy of their multiplicative combination remains a matter of discussion; the combination is adopted here and its consequences are examined in Sections 6 and 8.

**Classes of models.** Empirical models rely on regression relations obtained in field and wind-tunnel experiments, the classical example being the wind erosion equation [28] and its revised versions [29,30]. They are simple and fast, but their coefficients are valid only for the conditions of the underlying experiments, and they do not provide the space–time distribution of concentration at all. Semi-empirical schemes describe the physical mechanisms theoretically and parameterize individual coefficients from observations [13,15,16]; they are more universal but address emission rather than transport. Deterministic models describe transport by the advection–diffusion equation that follows from mass conservation [31] and remain the only class that provides the concentration field in the whole domain. The Eulerian approach yields this field directly on a grid [32], whereas the Lagrangian approach follows trajectories and is convenient for point sources and complex orography but requires many trajectories for stable statistics [33]. For an area source such as an eroding surface the Eulerian approach is preferable, and it is adopted here.

**Modelling systems.** The best known systems are HYSPLIT [33], CHIMERE [34] and WRF-Chem [35]. They couple emission and transport within mature platforms, have been extensively evaluated and perform well at synoptic scales. Their limitations for the present purposes are methodological rather than computational: their emission parameterizations are fixed and tuned mainly to the Sahara or the deserts of East Asia, their internal schemes are difficult to modify, and the size distribution is prescribed by a predefined set of modes. Regional studies note that such settings are not directly transferable to the specific dust and salt-laden material of the Aral Sea region [5,36]; a recent inventory also shows the large number and diversity of dust sources in Central Asia [37]. The closure relations used here—dry deposition by the resistance method [38–40], stability functions of the surface layer [41,42], and the terrain-following coordinate [43] with its known accuracy limitations [44]—are taken from established practice; well-posedness of problems of this class relies on the theory of parabolic equations [45], and the input fields are available from modern reanalyses [46,47].

**Previous work of the authors.** The present work continues earlier studies of the authors. In [48] a model of aerosol particle dispersion was constructed in which particle velocities depend on the particle mass, diameter and density; a nonlinear model for monitoring and forecasting harmful substances in the atmosphere and the influence of vegetation cover on transport were studied in [49,50], and efficient splitting-based algorithms for regional pollution problems were developed in [51,52]. These works considered industrial and generic aerosol sources; the coupling with a physically based wind-erosion emission scheme and the size-resolved treatment of mineral dust are new here.

**Open problem.** The comparison of the above directions shows that emission and transport are almost always separated: the emission flux is computed by a stand-alone block following [13–17] and passed to the transport model as a volume source in the surface layer, which requires the choice of an injection layer and treats emission and deposition by different model components. The size distribution, if resolved, is described by fractions with fixed settling velocities, whereas the variability of these velocities follows from the physics of the process [48,49]. Removing these two gaps is the subject of this paper.

# Problem Statement

The atmospheric domain over an arid territory is a rectangular parallelepiped whose lower face coincides with the underlying surface and whose upper face lies within the boundary layer, above the level at which the contribution of surface emission is practically exhausted. The problem is to find the space–time distribution of the mass concentration of dust particles of each fraction for a given wind field, surface state and soil size distribution.

The particles are divided into *N*~f~ fractions by equivalent diameter. The division reflects the fact that the regime of particle motion is determined by its size: coarse particles (larger than about 500 µm) move by creep and practically do not enter atmospheric transport, intermediate particles move by saltation, and fine particles (smaller than about 70 µm) become suspended and are transported over large distances [8,18,19]. The subject of modelling are the suspendable fractions; saltation is treated as the mechanism that supplies them.

The following assumptions are adopted.

1. Air is treated as an incompressible medium; the wind field is prescribed and satisfies the continuity equation. The feedback of dust on the flow is neglected, which is justified at the volume concentrations typical of the conditions considered.
2. Particles are spherical.
3. Fractions interact with the flow independently: coagulation and fragmentation are not considered, which is admissible at moderate concentrations and relatively short residence times.
4. Turbulent transport is described by gradient (K-theory) closure with a diagonal diffusion tensor aligned with the coordinate axes [31,42].
5. Wet deposition and chemical transformations are neglected, which is acceptable for arid territories with few precipitation days; dry deposition is prescribed by the surface boundary condition.

These assumptions restrict the model to regional and local problems in the absence of intense precipitation but retain a physically meaningful description of the size distribution and of variable particle velocities, which is the purpose of the model.


# Mathematical Model

The model is based on the conservation of mass of the admixture [31]. The main difference from the conventional formulation is the way emission is coupled with transport: the detachment flux enters not as a volume source but as a boundary condition at the underlying surface. In addition, the transport equation is written in a generalized form that admits the actual particle velocity; the classical form remains a limiting case.

## Transport Equation

For the concentration of the *i*-th fraction in Ω × (0, *T*],

$$\frac{\partial C_i}{\partial t}+\frac{\partial (v_{x,i}C_i)}{\partial x}+\frac{\partial (v_{y,i}C_i)}{\partial y}+\frac{\partial (v_{z,i}C_i)}{\partial z}=\frac{\partial}{\partial x}\left(K_x\frac{\partial C_i}{\partial x}\right)+\frac{\partial}{\partial y}\left(K_y\frac{\partial C_i}{\partial y}\right)+\frac{\partial}{\partial z}\left(K_z\frac{\partial C_i}{\partial z}\right)-\sigma_i C_i+f_i, \qquad (1)$$

where *C*~*i*~ is the mass concentration of the *i*-th fraction (kg/m^3^), *i* = 1, …, *N*~f~; *v*~*x,i*~, *v*~*y,i*~, *v*~*z,i*~ are the components of the particle transport velocity (m/s); *K*~*x*~, *K*~*y*~, *K*~*z*~ are the turbulent diffusion coefficients (m^2^/s); σ~*i*~ is the removal coefficient accounting for scavenging (s^−1^); and *f*~*i*~ represents volume sources of non-erosive origin (kg m^−3^ s^−1^).

## Particle Velocities

In most models the particle is assumed to move with the air velocity, and settling is introduced as a separate term. This neglects inertia: a particle leaving the surface does not acquire the flow velocity instantaneously. To delimit the range in which this simplification is valid, the particle velocity is determined explicitly [48]. The motion of a spherical particle of diameter *d*~*i*~ and density ρ~*p*~ is described by Newton's second law with Stokes drag,

$$\frac{d\mathbf{v}_i}{dt}=\frac{\mathbf{U}-\mathbf{v}_i}{\tau_{p,i}}+\mathbf{g}, \qquad \tau_{p,i}=\frac{\rho_p d_i^{2}}{18\mu}, \qquad (2)$$

where **U** is the wind velocity, **v**~*i*~ the particle velocity, μ the dynamic viscosity of air and τ~*p,i*~ the relaxation time. The initial condition reflects the discrete nature of detachment: the particle rests on the surface until the moment of entrainment and then relaxes towards the local flow velocity. In the implementation, system (2) is integrated at every transport time step by the three-stage scheme of Crank–Nicolson and BDF2 type [53] implemented in the DustVel program [54]; the scheme remains stable for the stiff system formed by fractions whose relaxation times differ by four orders of magnitude.

**Classical formulation as a limiting case.** For *v*~*x,i*~ = *u*, *v*~*y,i*~ = *v* and *v*~*z,i*~ = *w* − *w*~*g,i*~, Eq. (1) reduces to the conventional form, in which advection is performed with the air velocity and settling with velocity *w*~*g,i*~ is a separate term. The proposed model therefore contains the classical one [31,32] as a special case.

**Limits of applicability of the simplification.** Since the relaxation time is proportional to the square of the diameter, it differs by orders of magnitude between fractions. For particles of 2.5 µm (ρ~*p*~ = 1500 kg/m^3^), 10 µm (2000 kg/m^3^) and 50 µm (2500 kg/m^3^) it equals 0.029 ms, 0.61 ms and 19.2 ms, respectively [54]. At a wind speed of 10 m/s the corresponding horizontal lag *U*τ~*p*~ is 0.3 mm, 6.1 mm and 19 cm, i.e. negligible compared with any practical grid spacing. The inertial correction therefore matters only within the first metres after lift-off and for particles of several tens of micrometres and larger; for regional transport of the fine fractions the classical form is sufficient. This conclusion is quantified by the Stokes number in Section 6.

## Surface Boundary Condition

The key element of the formulation is the way emission is introduced. Instead of a volume source in the lowest grid layer, a boundary condition of the third kind is imposed at the underlying surface, relating the diffusive flux to the emission and dry-deposition fluxes:

$$K_z\left.\frac{\partial C_i}{\partial z}\right|_{z=h(x,y)}=-F_i+v_{d,i}\left.C_i\right|_{z=h(x,y)}, \qquad (3)$$

where *F*~*i*~ (kg m^−2^ s^−1^) is the emission flux of the *i*-th fraction, *v*~*d,i*~ the dry-deposition velocity and *h*(*x*, *y*) the terrain height. The first term on the right describes dust lifted by wind erosion, the second the return of particles to the surface. It is through this condition that the two stages of the process are combined into a single mathematical problem.

This formulation has two advantages over a volume source. First, the surface exchange is prescribed as a flux, so that no injection layer has to be chosen, and emission and deposition are treated by the same boundary relation: the sign of *F*~*i*~ − *v*~*d,i*~*C*~*i*~ determines whether the surface acts as a source or a sink at a given moment. Second, when the friction velocity falls below the threshold, *F*~*i*~ vanishes and condition (3) becomes a pure deposition condition; the regime change occurs continuously, without switching between models.

## Initial, Lateral and Top Conditions

At the initial moment a background distribution is prescribed:

$$C_i(x,y,z,0)=C_i^{0}(x,y,z), \qquad (x,y,z)\in\Omega. \qquad (4)$$

At the lateral and top boundaries, conditions of the third kind describe the exchange with the surrounding atmosphere:

$$K_n\left.\frac{\partial C_i}{\partial n}\right|_{\Gamma}=\gamma_i\left(C_i-C_i^{\mathrm{bg}}\right)_{\Gamma}, \qquad (5)$$

where Γ is the corresponding part of the boundary, *n* its outward normal, γ~*i*~ the exchange coefficient and $C_i^{\mathrm{bg}}$ the background concentration of the inflowing air. Condition (5) covers both limiting cases: γ~*i*~ = 0 gives a zero-flux condition, and γ~*i*~ → ∞ a prescribed concentration. This makes it possible to adapt the model to different physical situations without changing its structure [49], including nesting into a larger-scale model through $C_i^{\mathrm{bg}}$.

## Terrain-Following Coordinate

Terrain makes the lower boundary curvilinear, which hinders the direct use of finite-difference methods. The transformation [43]

$$\zeta=H\,\frac{z-h(x,y)}{H-h(x,y)} \qquad (6)$$

maps the domain onto a rectangular parallelepiped: the ground becomes the plane ζ = 0 and the top the plane ζ = *H*. The structure of Eq. (1) is preserved, but metric terms depending on the terrain gradients appear. The transformation has a known drawback: in regions of steep terrain the metric coefficients grow and the accuracy of horizontal gradients decreases [44]. The top *H* is kept constant in time: if it were identified with the diurnally varying boundary-layer depth, the coordinate would become time-dependent and an additional advective term would appear. Instead, *H* is chosen well above the expected maximum boundary-layer depth.

## Linear and Nonlinear Variants

In the linear variant the coefficients of Eq. (1) do not depend on concentration, the emission flux is a prescribed function of time and the fractions are independent, so that the system splits into *N*~f~ separate problems. In the nonlinear variant the particle velocities are obtained from system (2) and depend on the wind field, and the emission flux is a strongly nonlinear function of the friction velocity that changes with soil moisture; the nonlinearity of the problem is therefore concentrated at the boundary. Together with the parameterizations of Section 5, Eqs. (1)–(6) form a closed formulation (Fig. 1).

![Figure 1: Computational domain, terrain-following levels and boundary conditions](fig/Fig1.png)

# Parameterization of the Controlling Factors

Closure of the model requires the emission flux entering condition (3), the turbulent diffusion coefficients and the settling and dry-deposition velocities of each fraction. The emission scheme is the key element and is constructed in two steps: first the saltation flux is computed, then it is converted into the vertical flux of fine dust.

## Effective Threshold Friction Velocity

Fine particles (*d* < 20 µm) are not detached from the surface directly because of cohesion [15,19]. Their main source is the impact of saltating sand grains, which break soil aggregates and eject fine material. The calculation therefore starts from the threshold of saltating grains. All surface-state factors are combined into one effective value,

$$u_{*t}^{\mathrm{eff}}=u_{*t}^{0}(d_s)\,f_w(w)\,R_\lambda(\lambda), \qquad (7)$$

where $u_{*t}^{0}$ is the threshold for a dry bare surface given by the expression of Shao and Lu [23],

$$u_{*t}^{0}(d)=\sqrt{A_N\left(\frac{\rho_p g d}{\rho_a}+\frac{\gamma}{\rho_a d}\right)}, \qquad (8)$$

with *A*~*N*~ = 0.0123, γ = 3 × 10^−4^ kg/s^2^, ρ~*p*~ = 2650 kg/m^3^ and air density ρ~*a*~ = 1.225 kg/m^3^. Expression (8) has its minimum of 0.237 m/s at *d* ≈ 107 µm (Fig. 2A). The threshold is evaluated at the reference saltation diameter *d*~*s*~ = 75 µm, close to the experimentally observed minimum [22], where it equals 0.244 m/s, i.e. 3% above the minimum of (8).

The factor *f*~*w*~ accounts for soil moisture [24]:

$$f_w=\begin{cases}1, & w\le w',\\ \sqrt{1+1.21\,(w-w')^{0.68}}, & w>w',\end{cases} \qquad w'=0.0014\,c^{2}+0.17\,c, \qquad (9)$$

where *w* is the gravimetric soil moisture (%) and *c* the clay content (%). The factor *R*~λ~ describes the partition of shear stress between the erodible surface and roughness elements (vegetation and non-erodible elements) [25]:

$$R_\lambda=\sqrt{(1-m\sigma_r\lambda)(1+m\beta_r\lambda)}, \qquad (10)$$

with β~*r*~ = 90, σ~*r*~ = 1 and *m* = 0.5, where λ is the roughness density (frontal area index). Both factors are not smaller than unity, i.e. they only raise the threshold (Fig. 2B,C). The methodological advantage of form (7) is that all surface-state parameters are collected in a single effective value and can be varied uniformly.

![Figure 2: (A) Threshold friction velocity of a dry bare surface as a function of particle diameter, Eq. (8); (B) soil-moisture factor, Eq. (9), for three clay fractions; (C) drag-partition factor, Eq. (10)](fig/Fig2.png)

## From Saltation to Vertical Dust Flux

The friction velocity is obtained from the logarithmic profile,

$$u_*=\frac{\kappa U_{10}}{\ln(z_{\mathrm{ref}}/z_0)}, \qquad (11)$$

with κ = 0.4, *z*~ref~ = 10 m and aerodynamic roughness length *z*~0~. The horizontal saltation flux is given by the expression of White [11]:

$$Q=C_W\frac{\rho_a}{g}\,u_*^{3}\left(1-\frac{u_{*t}^{\mathrm{eff}}}{u_*}\right)\left(1+\frac{u_{*t}^{\mathrm{eff}}}{u_*}\right)^{2}, \qquad u_*>u_{*t}^{\mathrm{eff}}, \qquad (12)$$

with *C*~*W*~ = 2.61 and *Q* = 0 otherwise. The vertical dust flux is obtained through the sandblasting efficiency coefficient α, which grows exponentially with clay content [13], and the erodible fraction *A*~ef~ of the grid cell:

$$F=\alpha\,Q\,A_{\mathrm{ef}}, \qquad \alpha=10^{\,13.4\,m_{cl}-6}\ \mathrm{m}^{-1}, \qquad m_{cl}\le 0.2, \qquad (13)$$

where *m*~*cl*~ is the clay mass fraction; the cap reflects the saturation of the efficiency for clay-rich soils, whose aggregates are stronger. The exponential clay dependence in Eq. (13) follows Marticorena and Bergametti [13]; its dimensional prefactor is two orders of magnitude smaller than in the original relation, where α is expressed in cm^−1^. The prefactor therefore acts as an effective emission-efficiency coefficient for the surfaces considered; it was fixed before the observations of Section 8.7 were analysed and was not tuned to them. The resulting dependence of *F* on *u*~*~ is shown in Fig. 3.

![Figure 3: (A) Vertical dust flux as a function of friction velocity for several effective thresholds (clay fraction 0.05, *A*~ef~ = 1); (B) sandblasting efficiency as a function of clay content, Eq. (13)](fig/Fig3.png)

## Size-Resolved Emission

The total flux is insufficient, because particles of different size differ in settling velocity by orders of magnitude and follow completely different paths. The mass size distribution of the emitted dust is described by a sum of three lognormal modes,

$$\frac{dM}{d\ln d}=\sum_{j=1}^{3}\frac{\omega_j}{\sqrt{2\pi}\ln\sigma_j}\exp\left[-\frac{\ln^{2}(d/D_j)}{2\ln^{2}\sigma_j}\right], \qquad (14)$$

with median diameters *D*~*j*~ = 1.5, 6.7 and 45 µm, geometric standard deviations σ~*j*~ = 1.7, 1.6 and 1.5 and weights ω~*j*~ = 0.05, 0.40 and 0.55. The first two modes follow the emitted-aerosol modes of Alfaro et al. [16,17]; the third, coarse mode represents the short-range suspended fraction produced by sandblasting of sandy desert soils. Integration of (14) over the transport fractions gives the share *p*~*i*~ of each fraction and the fractional flux *F*~*i*~ = *p*~*i*~*F* entering condition (3). Five transport fractions are used (Table 1, Fig. 4A).

::: {custom-style="TSP Table Caption"}
Table 1: Transport fractions and their parameters
:::

| Fraction | Size range (µm) | Representative diameter (µm) | ρ~*p*~ (kg/m^3^) | Mass share *p*~*i*~ | τ~*p*~ (ms) | *w*~*g*~ (cm/s) |
|---|---|---|---|---|---|---|
| 1 (PM~2.5~) | 0.2–2.5 | 0.71 | 1500 | 0.049 | 0.0023 | 0.0023 |
| 2 (PM~10~) | 2.5–10 | 5.0 | 2000 | 0.327 | 0.15 | 0.15 |
| 3 | 10–20 | 14.1 | 2200 | 0.088 | 1.35 | 1.32 |
| 4 | 20–50 | 31.6 | 2400 | 0.327 | 7.37 | 7.23 |
| 5 | 50–100 | 70.7 | 2600 | 0.208 | 39.9 | 39.1 |

Note: The representative diameter is the geometric mean of the fraction bounds; τ~*p*~ and *w*~*g*~ refer to this diameter.

## Settling and Dry Deposition

The gravitational settling velocity follows from the balance of gravity and Stokes drag,

$$w_{g,i}=\frac{\rho_{p,i}\,g\,d_i^{2}}{18\mu}, \qquad (15)$$

evaluated at the representative diameter of each fraction. The values span more than four orders of magnitude, from 0.0023 cm/s to 39 cm/s (Table 1, Fig. 4B), which explains quantitatively why fine fractions travel far while coarse ones settle near the source. Stokes' law is valid for particle Reynolds numbers below about unity; for the coarsest fraction Re~*p*~ ≈ 1.8, and the standard drag correction would reduce its settling velocity by about 20%. This affects only the fraction that is deposited within a few kilometres of the source (Section 9).

![Figure 4: (A) Mass size distribution of emitted dust, Eq. (14), with fraction bounds (dashed) and mass shares; (B) settling velocity of the transport fractions, Eq. (15)](fig/Fig4.png)

The dry-deposition velocity is computed by the resistance method [38–40]:

$$v_{d,i}=w_{g,i}+\frac{1}{r_a+r_b+r_a r_b w_{g,i}}, \qquad r_a=\frac{\ln(z_{\mathrm{ref}}/z_0)}{\kappa u_*}, \qquad (16)$$

where *r*~*a*~ is the aerodynamic resistance (averaged over the domain) and *r*~*b*~ = 50 s/m the quasi-laminar sublayer resistance.

## Turbulent Diffusion and Wind Field

The vertical diffusion coefficient follows Monin–Obukhov similarity with a boundary-layer profile [41,42]:

$$K_z=\frac{\kappa u_* z}{\varphi_h(z/L)}\left(1-\frac{z}{h_{\mathrm{bl}}}\right)^{2}, \qquad \varphi_h=\begin{cases}1+5\,z/L, & z/L\ge 0,\\ (1-16\,z/L)^{-1/2}, & z/L<0,\end{cases} \qquad (17)$$

limited to 0.1 m^2^/s ≤ *K*~*z*~ ≤ 200 m^2^/s. In the present computations the Obukhov length *L* = −50 m and the boundary-layer depth *h*~bl~ = 1500 m are fixed, representing the unstable daytime conditions typical of dust events; the horizontal coefficients are *K*~*x*~ = *K*~*y*~ = 10^3^ m^2^/s. The horizontal wind follows a power-law profile, **U**~h~(*z*) = **U**~10~(*z*/*z*~ref~)^0.16^, with the 10-m wind taken from reanalysis, and the vertical component is recovered from the continuity equation,

$$w(z)=-\int_{h}^{z}\left(\frac{\partial u}{\partial x}+\frac{\partial v}{\partial y}\right)dz', \qquad (18)$$

which ensures conservation of air mass in the flow field.

# Properties of the Model

The formulation has several properties that determine its range of applicability and serve as correctness criteria for computations. They are derived here analytically.

**Integral mass budget.** Integrating Eq. (1) over Ω and applying the divergence theorem with the incompressibility of air and conditions (3) and (5) gives, for each fraction,

$$\frac{d}{dt}\int_{\Omega}C_i\,d\Omega=\int_{S}F_i\,dS-\int_{S}v_{d,i}C_i\,dS-\oint_{\Gamma}\gamma_i\left(C_i-C_i^{\mathrm{bg}}\right)d\Gamma-\sigma_i\int_{\Omega}C_i\,d\Omega+\int_{\Omega}f_i\,d\Omega, \qquad (19)$$

where *S* is the underlying surface and Γ the lateral and top boundaries. The change of mass in the domain equals the input by emission minus dry deposition, exchange through the outer boundaries and volume removal. Emission enters as a surface integral determined by the surface state only; relation (19) also serves as a test of the numerical algorithm, whose budget residual must not exceed the scheme error.

**Non-negativity.** If the initial distribution, the background concentration of the inflowing air and the sources are non-negative, the solution remains non-negative for all *t* > 0. This follows from the maximum principle for parabolic equations [45]: at a point of a negative interior minimum the time derivative and the diffusion term have signs incompatible with the equation. A negative minimum is also impossible at the surface: for *C*~*i*~ = 0 condition (3) gives a non-negative diffusive flux directed into the domain, because *F*~*i*~ ≥ 0. A numerical scheme should inherit this property; the discrete behaviour is discussed in Section 7.

**Continuity of the regime transition.** The emission flux is defined piecewise and vanishes for *u*~*~ ≤ $u_{*t}^{\mathrm{eff}}$. By Eq. (12), *Q* = *C*~*W*~ρ~*a*~*g*^−1^(*u*~*~ − *u*~*t*~)(*u*~*~ + *u*~*t*~)^2^ above the threshold; it tends to zero at the threshold, so that *F*~*i*~ is a continuous, piecewise-smooth and locally Lipschitz function of the friction velocity (its derivative jumps from 0 to 4*C*~*W*~ρ~*a*~*u*~*t*~^2^/*g* at the threshold). The right-hand side of condition (3) is therefore continuous, and when the wind fluctuates near the threshold—a typical situation at the beginning and end of a dust storm—the surface flux does not jump. This is what allows emission and deposition to be described by one condition without switching between models.

**Dimensionless numbers.** Scaling Eq. (1) with a horizontal scale *L*~*x*~, a velocity scale *U* and the boundary-layer depth *H*~bl~, the transport regime is determined by three numbers:

$$\mathrm{Pe}=\frac{UL_x}{K_x}, \qquad \mathrm{Se}_i=\frac{w_{g,i}L_x}{UH_{\mathrm{bl}}}, \qquad \mathrm{St}_i=\frac{\tau_{p,i}U}{L_x}. \qquad (20)$$

For the regional problem of Section 8 (*U* = 10 m/s, *L*~*x*~ = 380 km, *K*~*x*~ = 10^3^ m^2^/s, *H*~bl~ = 1.5 km) the Péclet number is about 4 × 10^3^, and the grid Péclet number *U*Δ*x*/*K*~*x*~ is about 60, i.e. transport is strongly advection-dominated. This has a direct consequence for the algorithm: schemes with central differences for the convective terms lose monotonicity at such Péclet numbers [55]. The settling parameter Se~*i*~ shows whether a particle settles within the domain length: it ranges from 6 × 10^−4^ for the finest to about 10 for the coarsest fraction, which quantitatively justifies abandoning a single-mode description. The Stokes number St~*i*~ does not exceed 10^−4^ at the grid scale for any fraction, so that the simplification **v**~*i*~ = **U** is justified for regional transport, in agreement with the estimates of Section 4.2.

**Limiting cases.** The model contains known formulations as special cases, which serves as a consistency check. For *v*~*x,i*~ = *u*, *v*~*y,i*~ = *v*, *v*~*z,i*~ = *w* − *w*~*g,i*~ Eq. (1) reduces to the classical form with a separate settling term. For γ~*i*~ = 0 condition (5) gives zero flux through the boundary, and for γ~*i*~ → ∞ a prescribed concentration. For *N*~f~ = 1, constant coefficients, flat terrain, a steady uniform flow and a point source instead of areal emission the solution reduces to the classical Gaussian plume. For *u*~*~ below the threshold, condition (3) becomes a pure deposition condition. These transitions allow the numerical algorithm to be verified step by step, starting from problems with known solutions.

# Numerical Implementation

The model is implemented in the DustFlow program complex; the construction and analysis of the numerical algorithm are the subject of a companion paper, and only its main features are summarized here. The transport equation is written in conservative form in the terrain-following coordinate (6), with the metric factor *H* − *h* included in the fluxes. Directional splitting reduces each time step to a sequence of one-dimensional problems in *x*, *y* and ζ [56,57]. In each one-dimensional step the diffusion and upwind advection operators are discretized implicitly by the Crank–Nicolson scheme [53], and the resulting tridiagonal systems are solved by the Thomas algorithm [55], vectorized over all grid lines. A second-order flux-limited antidiffusive correction with the van Leer limiter [58] is added explicitly to the upwind fluxes, which keeps the scheme essentially monotone at the high Péclet numbers found above. Boundary conditions (3) and (5) are discretized consistently with the Crank–Nicolson averaging, and the net fluxes through all boundaries are accumulated to evaluate budget (19) at every step. Small negative undershoots that the limited scheme can still produce at very steep gradients are set to zero; the corresponding mass is accounted for explicitly in the budget. The particle velocities are updated at every step from system (2), and the meteorological forcing is updated hourly while the concentration field and the budget are carried over continuously. With constant forcing, a run split into one-hour segments reproduces an uninterrupted run bit for bit.


# Computational Experiment

## Study Area and Input Data

The computations were performed for the Bukhara region of Uzbekistan and the adjacent part of the Kyzylkum desert, 61.5°–66.0° E, 38.5°–42.0° N (Fig. 5). About 72% of the area is bare or sparsely vegetated desert, 15% steppe grassland and 9% irrigated cropland of the Zarafshan oasis and the Amu Darya valley. Hourly 10-m wind, 2-m temperature and volumetric soil moisture of the 0–7 cm layer were taken from the ERA5-Land reanalysis (0.1°) [46]. Clay content and bulk density of the 0–5 cm layer were taken from SoilGrids 2.0 (250 m) [59], terrain from the Copernicus GLO-90 digital elevation model [60], and land cover from ESA WorldCover 2021 (10 m) [61]. Land-cover classes were converted into *z*~0~, λ and *A*~ef~ (bare or sparse vegetation: *z*~0~ = 10^−3^ m, λ = 0.004, *A*~ef~ = 0.25; grassland and shrubland: *z*~0~ = 0.03–0.05 m, λ = 0.03–0.05, *A*~ef~ = 0.10; built-up areas, trees and water: *A*~ef~ = 0). Volumetric moisture θ was converted into gravimetric moisture by *w* = 100 θρ~*w*~/ρ~*b*~ with the SoilGrids bulk density ρ~*b*~.

Two data-quality issues required decisions. First, SoilGrids assigns about 30% clay to all land-cover classes of the domain, including the sandy desert, with a 90% prediction interval of 2%–80%, i.e. it carries practically no information there; since the clay fraction is one of the most influential parameters (Section 8.6), literature values for Kyzylkum sandy soils were used for bare surfaces (*m*~*cl*~ = 0.05) and grassland and shrubland (0.08), and SoilGrids values were retained elsewhere. Second, ERA5-Land does not represent irrigation, so that its soil moisture over the oases is too low; irrigated cropland was therefore excluded from the erodible surface during the growing season (*A*~ef~ = 0). Both decisions were made on physical grounds before the model results were compared with observations.

![Figure 5: Static input fields on the 0.01° intermediate grid: (A) terrain elevation; (B) clay fraction; (C) erodible fraction *A*~ef~; (D) aerodynamic roughness length. Sources: Copernicus GLO-90, SoilGrids 2.0, ESA WorldCover 2021](fig/Fig5.png)

## Computational Setup

The dust storm of 28–29 April 2025 was selected. It was the strongest event over Bukhara in the CAMS reanalysis for March–May 2025 and is documented by the national hydrometeorological service. The storm was driven by northerly winds of 10–13 m/s. The computational parameters are listed in Table 2. The domain of 380 km × 390 km × 5 km was covered by a 60 × 60 × 20 grid (Δ*x* = 6.3 km, Δ*y* = 6.5 km) with a time step of 120 s. The simulation covered 48 h (28 April 00:00 – 30 April 00:00 UTC) with hourly updates of the meteorological forcing. The background concentration at the lateral boundaries was set to zero, so that only emission within the domain was represented. The computation took 228 s on a single processor core (4.7 s per model hour).

::: {custom-style="TSP Table Caption"}
Table 2: Computational setup
:::

| Parameter | Value |
|---|---|
| Domain | 61.5°–66.0° E, 38.5°–42.0° N; 380 km × 390 km × 5 km |
| Grid | 60 × 60 × 20; Δ*x* = 6.3 km, Δ*y* = 6.5 km |
| Time step, simulation period | 120 s; 48 h (28 April 2025 00:00 – 30 April 00:00 UTC) |
| Meteorological forcing | ERA5-Land, hourly update |
| Transport fractions | 5 (Table 1) |
| Diffusion | Eq. (17), *L* = −50 m, *h*~bl~ = 1500 m; *K*~*x*~ = *K*~*y*~ = 10^3^ m^2^/s |
| Lateral background | $C_i^{\mathrm{bg}}$ = 0 (local emission only) |

## Emission and Concentration Fields

Table 3 characterizes the emission at four instants: a calm reference day and three hours of the storm. On the calm day the threshold is not exceeded anywhere, and the emission is identically zero; the model generates neither mass nor numerical oscillations. During the storm the eroding area changes from 44% to 74% of the domain within hours, which justifies time-dependent forcing.

::: {custom-style="TSP Table Caption"}
Table 3: Emission characteristics at selected hours
:::

| Instant (UTC) | Maximum *U*~10~ (m/s) | Median desert soil moisture (%) | Eroding area (%) | Emission (t/h) |
|---|---|---|---|---|
| 23 April 09:00 (calm) | 5.8 | 2.4 | 0 | 0 |
| 28 April 21:00 (onset) | 12.3 | 2.2 | 46.5 | 27 800 |
| 29 April 09:00 (storm) | 12.2 | 2.2 | 73.6 | 42 900 |
| 29 April 15:00 (peak) | 12.7 | 2.2 | 43.5 | 34 700 |

The emission and near-surface concentration fields at 29 April, 12:00 UTC are shown in Fig. 6. At this hour *u*~*~ ranges from 0.26 to 1.58 m/s over the domain, and the effective threshold from 0.24 to 2.4 m/s. The threshold is close to its dry-surface value in the desert and is raised several-fold by moisture and roughness corrections in the oasis and the mountains. Emission occurs over 70% of the domain, with a maximum flux of 9.7 × 10^−6^ kg m^−2^ s^−1^. The emission is spatially very heterogeneous: the most active sources lie along the northern margin of the Bukhara oasis, at the transition between desert and oasis, where the wind is strong and the surface bare. The concentration field shows narrow plumes elongated along the wind from each active source, with the highest concentrations south of the oasis margin. The domain-mean near-surface concentration (all fractions) is 513 µg/m^3^ and the 99th percentile 3756 µg/m^3^. Over the 48 h, 1000.8 kt of dust was emitted from the domain, of which 537.6 kt originated from the Bukhara region proper (40 100 km^2^).

![Figure 6: (A) Dust emission flux and (B) near-surface dust concentration on 29 April 2025, 12:00 UTC; arrows show the 10-m wind, stars the monitoring stations](fig/Fig6.png)

## Mass Budget and Model Checks

The budget (19) was evaluated at every time step (Fig. 7). Of the emitted mass, 62.1% left the domain through its boundaries, 37.2% was deposited and 0.6% was removed by scavenging, while 2.2% remained airborne at the end. The relative residual of the budget stayed below 0.01% throughout and was 0.0029% at the end. The zeroing of negative undershoots (Section 7) added 20.7 kt, i.e. 2.1% of the emitted mass. This term is accounted for exactly in the budget, and its reduction is one of the directions for improving the scheme. Because the forcing varies in time, the dust mass in the domain does not reach a steady state: it grows with the storm, peaks at 78.7 kt on 29 April at 13:00 UTC and decreases as the wind weakens.

![Figure 7: (A) Components of the mass budget, Eq. (19), during the storm; (B) relative residual of the budget](fig/Fig7.png)

## Fraction-Resolved vs. Single-Mode Transport

This is the main result of the experiment. The same 48-h simulation was repeated with the five transport fractions replaced by a single effective mode covering 0.2–100 µm, with a representative diameter of 4.5 µm and a settling velocity of 0.09 cm/s. The emission scheme and the total emitted mass (1000.8 kt) are identical in both runs; the fate of this mass differs radically (Table 4, Fig. 8).

::: {custom-style="TSP Table Caption"}
Table 4: Fate of the emitted dust after 48 h: five transport fractions vs. a single effective mode
:::

| Quantity | Five fractions | Single mode | Ratio |
|---|---|---|---|
| Emitted (kt) | 1000.8 | 1000.8 | 1.00 |
| Dry-deposited (kt) | 372.6 | 73.2 | 5.09 |
| Exported through boundaries (kt) | 621.2 | 905.6 | 0.69 |
| Airborne at the end (kt) | 21.8 | 31.0 | 0.70 |
| Near-surface concentration, 48-h mean over the domain (µg/m^3^) | 205 | 252 | 0.81 |
| Near-surface concentration, 29 April 12:00 UTC, domain mean (µg/m^3^) | 513 | 625 | 0.82 |
| Budget residual (%) | 0.0029 | 0.0041 | — |

The single-mode description underestimates dry deposition by a factor of 5.1 and, consequently, overestimates both the export from the domain and the near-surface concentration. The relative difference of the 48-h mean concentration is +21% in the median over the domain and reaches +38% over one tenth of it; at the Bukhara station it is +27%. The reason is visible in Table 1: the effective mode reproduces the behaviour of the two finest fractions only, while the coarse fractions, which account for most of the deposition, are lost.

Not only the numbers but also the structure of the solution differ. In the fraction-resolved run the contributions of the fractions to the near-surface concentration are 6%, 40%, 11%, 34% and 10%, respectively: the field is formed by two physically different groups, a fine group transported across the whole domain and a coarse group settling near the sources. The single-mode approximation replaces this two-component structure by one intermediate component, and no choice of an effective diameter can correct this. Moreover, a single mode cannot provide the PM~2.5~/PM~10~ ratio at all, which is a primary quantity for air-quality applications (Section 8.7).

![Figure 8: 48-h mean near-surface concentration computed with (A) five transport fractions and (B) a single effective mode; (C) relative difference; (D) fate of the emitted mass](fig/Fig8.png)

## Sensitivity to the Controlling Parameters

Each parameter was varied by ±25% from its base value with the others fixed, for the forcing of 29 April 2025, 09:00 UTC held constant over 6 h on a reduced grid. The sensitivity index was defined as

$$S_p=\frac{\max\left(|\Delta \bar C^{+}|,\,|\Delta \bar C^{-}|\right)/\bar C}{|\Delta p|/p}, \qquad (21)$$

where $\bar C$ is the domain-mean near-surface concentration (Table 5, Fig. 9).

::: {custom-style="TSP Table Caption"}
Table 5: Sensitivity of the domain-mean near-surface concentration to the controlling parameters
:::

| Parameter | −25% | +25% | *S*~*p*~ |
|---|---|---|---|
| Wind speed *U*~10~ | −76.4% | +150.0% | 6.00 |
| Clay fraction *m*~*cl*~ | −66.8% | +109.9% | 4.40 |
| Soil moisture *w* | +29.0% | −29.0% | 1.16 |
| Erodible fraction *A*~ef~ | −25.0% | +25.0% | 1.00 |
| Roughness length *z*~0~ | −22.0% | +20.7% | 0.88 |
| Roughness density λ | +11.6% | −11.7% | 0.47 |
| Terrain elevation *h* | +0.1% | +0.3% | 0.01 |

![Figure 9: Change of the domain-mean near-surface concentration for ±25% variation of each parameter](fig/Fig9.png)

The wind speed is the dominant factor: a 25% increase raises the concentration by a factor of 2.5, owing to the cubic dependence (12) combined with the threshold nature of the emission. Near the threshold the forecast therefore inherits the error of the wind field with strong amplification, and the requirements on the accuracy of meteorological input are especially strict there. The clay fraction is the second factor (*S*~*p*~ = 4.4), because the sandblasting efficiency (13) depends on it exponentially; this quantifies the need for field data on soil texture, which the global soil database does not provide for the Kyzylkum. Soil moisture and roughness density act in the opposite direction, raising the threshold. The index for *A*~ef~ equals unity exactly, as expected from the linear dependence (13), which serves as a control of the implementation. The effect of terrain is negligible because the region is flat.

## Comparison with Observations

Hourly PM~10~ and PM~2.5~ concentrations measured by the automatic monitoring stations of the Hydrometeorological Service of Uzbekistan in Bukhara, Navoi and Karshi were used, together with the CAMS EAC4 reanalysis [62] as an independent model reference. Because the stations measure the total particulate concentration, including traffic, construction and industrial contributions, whereas the model computes wind-erosion dust only, the model was compared with the excess over background. The background was taken as the median of 20–26 April for the stations and, separately, for CAMS. For comparability, all three data sets were sampled at the 3-hourly CAMS times of 28–30 April. The model run for this comparison used the same configuration with a 24-h spin-up (from 27 April 00:00 UTC).

The results are summarized in Table 6 and Fig. 10. At Bukhara the model reproduces the onset of the storm on the evening of 28 April within about an hour and the temporal evolution with a correlation of 0.50, comparable to that of CAMS (0.64). Both the model and CAMS overestimate the storm-day mean excess, by factors of 1.4 and 1.7, respectively. The most distinctive result concerns the size composition. During the storm the observed PM~2.5~/PM~10~ ratio varied between 0.13 and 0.21 (median 0.16); the fraction-resolved model gives 0.13, within the observed range, whereas CAMS gives 0.48, more than twice the largest observed value. The observations show that the storm dust, and even the urban background, consists mainly of coarse mineral particles, while CAMS overestimates the fine fraction and underestimates the background by a factor of two. A single-mode model cannot address this question at all. The PM~2.5~/PM~10~ ratio thus provides direct observational support for the size resolution that is the main subject of this paper.

::: {custom-style="TSP Table Caption"}
Table 6: Comparison with station observations during 28–30 April 2025 (excess over background, 3-hourly values)
:::

| Quantity | Observed | Model | CAMS |
|---|---|---|---|
| Bukhara: storm-day mean excess PM~10~ (µg/m^3^) | 300 | 427 | 516 |
| Bukhara: correlation with observations | — | 0.50 | 0.64 |
| Bukhara: storm PM~2.5~/PM~10~ ratio | 0.13–0.21 (median 0.16) | 0.13 | 0.48 |
| Background PM~10~ at Bukhara (µg/m^3^) | 72 | — | 35 |
| Three stations: fraction within a factor of two (FAC2) | — | 0.11 | 0.24 |

Over the three stations together, neither the model nor CAMS reaches the value FAC2 > 0.5 commonly used as an acceptance criterion for air-quality models [63]. The local-only model underestimates the dust at Navoi and Karshi, where a large part of it is advected from outside the domain or originates from local urban sources. Nesting the model into CAMS through the background term of condition (5) improves the agreement there, but imports the fine-mode bias of CAMS (the ratio at Bukhara rises to 0.23). A detailed regional evaluation, including the nesting, is presented in a companion paper.

![Figure 10: (A) Observed excess PM~10~ at Bukhara (shaded), model and CAMS on 28–30 April 2025; (B) PM~2.5~/PM~10~ ratio of storm dust: observed hourly range and median, model and CAMS](fig/Fig10.png)

# Discussion and Limitations

The experiment confirms the internal consistency of the model and its physically meaningful response to the controlling parameters, and it shows a clear benefit of size resolution. The following limitations should be kept in mind.

First, the prefactor of the sandblasting efficiency (13) acts as an effective emission coefficient, and the clay fraction to which the emission is most sensitive after wind speed had to be taken from the literature for the desert. The overestimation of the storm-day mean at Bukhara by a factor of 1.4 is consistent with an emission bias of the sources located directly upwind of the station, on the northern margin of the oasis (Fig. 6A). Systematic calibration of the emission coefficient on a set of events and independent verification on another set is planned.

Second, the stability parameters in Eq. (17) are fixed at typical daytime values, so that the diurnal cycle of turbulent mixing is not represented; this is a likely reason why the model disperses the dust more slowly than observed after the storm (Fig. 10A).

Third, Stokes' law overestimates the settling velocity of the coarsest fraction by about 20%, which affects the near-source deposition only.

Fourth, the ERA5-Land soil moisture refers to the 0–7 cm layer, whereas erosion is controlled by the uppermost millimetres. In a winter event (February 2026) the model produced no emission because the reanalysis moisture exceeded the threshold, although dust was observed at Bukhara. A correction for the moisture of the surface layer is therefore needed for cold-season applications.

Fifth, the model represents the 6-km cell average, whereas urban stations are also influenced by sub-grid local sources, which limits the point-wise comparison.

# Conclusions

A three-dimensional non-stationary model of wind erosion and atmospheric dust loading has been developed in which emission and transport form a single boundary-value problem. The vertical detachment flux enters the formulation as a boundary condition of the third kind at the underlying surface, where it is balanced by dry deposition. Emission and deposition are therefore described by one boundary relation, the direction of the surface exchange follows from the sign of their difference, and the regime transition is continuous. The dust is resolved into transport fractions whose settling velocities differ by more than four orders of magnitude.

The transport equation is written in a generalized form that admits the actual particle velocity obtained from the relaxation equations; the classical form is its limiting case. For the PM~2.5~ and PM~10~ fractions the particle lag behind the flow is negligible, and it becomes noticeable only for particles of several tens of micrometres near the source. This methodological result delimits the range in which the classical form is sufficient.

All surface-state factors are combined into a single effective threshold friction velocity. The properties of the model—the integral mass budget, non-negativity, continuity of the surface flux with respect to the friction velocity, limiting cases and the governing dimensionless numbers—have been established analytically.

A 48-h simulation of the dust storm of 28–29 April 2025 over the Bukhara region with reanalysis meteorology and global soil and land-cover data satisfied the mass budget to within 0.003%. Replacing the five transport fractions by a single effective mode changed dry deposition by a factor of 5.1 and increased the near-surface concentration by 21% in the median and up to 38%; no choice of an effective diameter can reproduce the two-component structure of the field. Wind speed and soil clay content were found to be the dominant parameters. Compared with station observations, the model reproduced the onset and evolution of the storm at Bukhara with a skill comparable to the operational CAMS reanalysis. It also reproduced the observed PM~2.5~/PM~10~ ratio of storm dust (0.13 against 0.13–0.21 observed), where CAMS gave 0.48. Further work will address the calibration of the emission coefficient, a time-dependent boundary-layer stability and a surface-moisture correction.

::: {custom-style="TSP Back Matter"}
**Acknowledgement:** The authors thank the Copernicus Climate Change Service and the Copernicus Atmosphere Monitoring Service for the ERA5-Land and CAMS data, ISRIC—World Soil Information for SoilGrids, the European Space Agency for WorldCover and the Copernicus DEM, and the Hydrometeorological Service of the Republic of Uzbekistan for the monitoring data. During the preparation of this manuscript, the authors used Claude (Anthropic) for translation and language editing, for assistance in drafting and restructuring parts of the text, and for writing scripts for data processing and figure preparation. The authors subsequently reviewed and revised the relevant content and accept full responsibility for the article.

**Funding Statement:** The authors received no specific funding for this study.

**Author Contributions:** The authors confirm contribution to the paper as follows: Conceptualization, Tursun Shafiyev and Normakhmad Ravshanov; methodology, Madina Bobojonova and Tursun Shafiyev; software, Tursun Shafiyev and Madina Bobojonova; validation, Madina Bobojonova; formal analysis, Madina Bobojonova; investigation, Madina Bobojonova; data curation, Madina Bobojonova; writing—original draft preparation, Madina Bobojonova; writing—review and editing, Tursun Shafiyev and Normakhmad Ravshanov; visualization, Madina Bobojonova; supervision, Tursun Shafiyev and Normakhmad Ravshanov. All authors reviewed the results and approved the final version of the manuscript.

**Availability of Data and Materials:** This study used publicly available data: ERA5-Land hourly data from the Copernicus Climate Data Store (doi:10.24381/cds.e2161bac), CAMS EAC4 reanalysis from the Atmosphere Data Store (doi:10.24381/d58bbf47), SoilGrids 2.0, ESA WorldCover 2021 (doi:10.5281/zenodo.7254221) and Copernicus GLO-90. Station data are available from the monitoring portal of the Hydrometeorological Service of Uzbekistan. The DustVel program is openly available at doi:10.5281/zenodo.22735087. The source code of DustFlow and the scripts used to produce the results are available from the corresponding author upon reasonable request.

**Ethics Approval:** Not applicable.

**Conflicts of Interest:** The authors declare no conflicts of interest to report regarding the present study.
:::


# References {-}

1. Shao Y, Wyrwoll KH, Chappell A, Huang J, Lin Z, McTainsh GH, et al. Dust cycle: an emerging core theme in Earth system science. Aeolian Res. 2011;2(4):181–204. doi:10.1016/j.aeolia.2011.02.001.
2. Prospero JM, Ginoux P, Torres O, Nicholson SE, Gill TE. Environmental characterization of global sources of atmospheric soil dust identified with the NIMBUS 7 Total Ozone Mapping Spectrometer (TOMS) absorbing aerosol product. Rev Geophys. 2002;40(1):1002. doi:10.1029/2000RG000095.
3. Ginoux P, Prospero JM, Gill TE, Hsu NC, Zhao M. Global-scale attribution of anthropogenic and natural dust sources and their emission rates based on MODIS Deep Blue aerosol products. Rev Geophys. 2012;50(3):RG3005. doi:10.1029/2012RG000388.
4. Banks JR, Heinold B, Schepanski K. Impacts of the desiccation of the Aral Sea on the Central Asian dust life-cycle. J Geophys Res Atmos. 2022;127(21):e2022JD036618. doi:10.1029/2022JD036618.
5. Indoitu R, Orlovsky L, Orlovsky N. Dust storms in Central Asia: spatial and temporal variations. J Arid Environ. 2012;85:62–70. doi:10.1016/j.jaridenv.2012.03.018.
6. Rakhmatova N, Nishonov BE, Shardakova L, Akhmedova A, Khudoyberdiev A, Rakhmatova V, et al. Temporal and spatial dynamics of dust storms in Uzbekistan from meteorological station records (2010–2023). Atmosphere. 2025;16(7):782. doi:10.3390/atmos16070782.
7. Nishonov BE, Kholmatjanov BM, Labzovskii LD, Rakhmatova N, Shardakova L, Abdulakhatov EI, et al. Study of the strongest dust storm occurred in Uzbekistan in November 2021. Sci Rep. 2023;13:20042. doi:10.1038/s41598-023-42256-1.
8. Bagnold RA. The physics of blown sand and desert dunes. London: Methuen; 1941.
9. Owen PR. Saltation of uniform grains in air. J Fluid Mech. 1964;20(2):225–42. doi:10.1017/S0022112064001173.
10. Kawamura R. Study of sand movement by wind. Rep Inst Sci Technol Univ Tokyo. 1951;5(3–4):95–112.
11. White BR. Soil transport by winds on Mars. J Geophys Res. 1979;84(B9):4643–51. doi:10.1029/JB084iB09p04643.
12. Chepil WS. Dynamics of wind erosion: I. Nature of movement of soil by wind. Soil Sci. 1945;60(4):305–20.
13. Marticorena B, Bergametti G. Modeling the atmospheric dust cycle: 1. Design of a soil-derived dust emission scheme. J Geophys Res. 1995;100(D8):16415–30. doi:10.1029/95JD00690.
14. Gillette DA, Passi R. Modeling dust emission caused by wind erosion. J Geophys Res. 1988;93(D11):14233–42. doi:10.1029/JD093iD11p14233.
15. Shao Y, Raupach MR, Findlater PA. Effect of saltation bombardment on the entrainment of dust by wind. J Geophys Res. 1993;98(D7):12719–26. doi:10.1029/93JD00396.
16. Alfaro SC, Gaudichet A, Gomes L, Maillé M. Modeling the size distribution of a soil aerosol produced by sandblasting. J Geophys Res. 1997;102(D10):11239–49. doi:10.1029/97JD00403.
17. Alfaro SC, Gomes L. Modeling mineral aerosol production by wind erosion: emission intensities and aerosol size distributions in source areas. J Geophys Res. 2001;106(D16):18075–84. doi:10.1029/2000JD900339.
18. Shao Y. Physics and modelling of wind erosion. 2nd ed. Dordrecht: Springer; 2008. doi:10.1007/978-1-4020-8895-7.
19. Kok JF, Parteli EJR, Michaels TI, Karam DB. The physics of wind-blown sand and dust. Rep Prog Phys. 2012;75(10):106901. doi:10.1088/0034-4885/75/10/106901.
20. Kok JF, Mahowald NM, Fratini G, Gillies JA, Ishizuka M, Leys JF, et al. An improved dust emission model—Part 1: model description and comparison against measurements. Atmos Chem Phys. 2014;14(23):13023–41. doi:10.5194/acp-14-13023-2014.
21. Shao Y, Ishizuka M, Mikami M, Leys JF. Parameterization of size-resolved dust emission and validation with measurements. J Geophys Res. 2011;116(D8):D08203. doi:10.1029/2010JD014527.
22. Iversen JD, White BR. Saltation threshold on Earth, Mars and Venus. Sedimentology. 1982;29(1):111–9. doi:10.1111/j.1365-3091.1982.tb01713.x.
23. Shao Y, Lu H. A simple expression for wind erosion threshold friction velocity. J Geophys Res. 2000;105(D17):22437–43. doi:10.1029/2000JD900304.
24. Fécan F, Marticorena B, Bergametti G. Parametrization of the increase of the aeolian erosion threshold wind friction velocity due to soil moisture for arid and semi-arid areas. Ann Geophys. 1999;17(1):149–57. doi:10.1007/s00585-999-0149-7.
25. Raupach MR, Gillette DA, Leys JF. The effect of roughness elements on wind erosion threshold. J Geophys Res. 1993;98(D2):3023–9. doi:10.1029/92JD01922.
26. Marticorena B, Bergametti G, Gillette D, Belnap J. Factors controlling threshold friction velocity in semiarid and arid areas of the United States. J Geophys Res. 1997;102(D19):23277–87. doi:10.1029/97JD01303.
27. Chatenet B, Marticorena B, Gomes L, Bergametti G. Assessing the microped size distributions of desert soils erodible by wind. Sedimentology. 1996;43(5):901–11. doi:10.1111/j.1365-3091.1996.tb01509.x.
28. Woodruff NP, Siddoway FH. A wind erosion equation. Soil Sci Soc Am Proc. 1965;29(5):602–8.
29. Fryrear DW, Bilbro JD, Saleh A, Schomberg H, Stout JE, Zobeck TM. RWEQ: improved wind erosion technology. J Soil Water Conserv. 2000;55(2):183–9.
30. Fryrear DW. Soil losses by wind erosion. Soil Sci Soc Am J. 1995;59(3):668–72.
31. Marchuk GI. Mathematical modelling in environmental problems. Moscow: Nauka; 1982 (In Russian).
32. Ginoux P, Chin M, Tegen I, Prospero JM, Holben B, Dubovik O, et al. Sources and distributions of dust aerosols simulated with the GOCART model. J Geophys Res. 2001;106(D17):20255–73. doi:10.1029/2000JD000053.
33. Stein AF, Draxler RR, Rolph GD, Stunder BJB, Cohen MD, Ngan F. NOAA's HYSPLIT atmospheric transport and dispersion modeling system. Bull Am Meteorol Soc. 2015;96(12):2059–77. doi:10.1175/BAMS-D-14-00110.1.
34. Menut L, Bessagnet B, Khvorostyanov D, Beekmann M, Blond N, Colette A, et al. CHIMERE 2013: a model for regional atmospheric composition modelling. Geosci Model Dev. 2013;6(4):981–1028. doi:10.5194/gmd-6-981-2013.
35. Grell GA, Peckham SE, Schmitz R, McKeen SA, Frost G, Skamarock WC, et al. Fully coupled "online" chemistry within the WRF model. Atmos Environ. 2005;39(37):6957–75. doi:10.1016/j.atmosenv.2005.04.027.
36. Opp C, Groll M, Aslanov I, Lotz T, Vereshagina N. Aeolian dust deposition in the southern Aral Sea region (Uzbekistan): ground-based monitoring results from the LUCA project. Quat Int. 2017;429:86–99.
37. Nobakht M, Shahgedanova M, White K. New inventory of dust emission sources in Central Asia and northwestern China derived from MODIS imagery using dust enhancement technique. J Geophys Res Atmos. 2021;126(4):e2020JD033382. doi:10.1029/2020JD033382.
38. Wesely ML. Parameterization of surface resistances to gaseous dry deposition in regional-scale numerical models. Atmos Environ. 1989;23(6):1293–304. doi:10.1016/0004-6981(89)90153-4.
39. Slinn WGN. Predictions for particle deposition to vegetative canopies. Atmos Environ. 1982;16(7):1785–94. doi:10.1016/0004-6981(82)90271-2.
40. Seinfeld JH, Pandis SN. Atmospheric chemistry and physics: from air pollution to climate change. 3rd ed. Hoboken: Wiley; 2016.
41. Businger JA, Wyngaard JC, Izumi Y, Bradley EF. Flux-profile relationships in the atmospheric surface layer. J Atmos Sci. 1971;28(2):181–9. doi:10.1175/1520-0469(1971)028<0181:FPRITA>2.0.CO;2.
42. Stull RB. An introduction to boundary layer meteorology. Dordrecht: Kluwer Academic Publishers; 1988. doi:10.1007/978-94-009-3027-8.
43. Phillips NA. A coordinate system having some special advantages for numerical forecasting. J Meteorol. 1957;14(2):184–5. doi:10.1175/1520-0469(1957)014<0184:ACSHSS>2.0.CO;2.
44. Mesinger F. On the convergence and error problems of the calculation of the pressure gradient force in sigma coordinate models. Geophys Astrophys Fluid Dyn. 1982;19(1–2):105–17. doi:10.1080/03091928208208949.
45. Ladyzhenskaya OA, Solonnikov VA, Uraltseva NN. Linear and quasilinear equations of parabolic type. Providence: American Mathematical Society; 1968.
46. Muñoz-Sabater J, Dutra E, Agustí-Panareda A, Albergel C, Arduini G, Balsamo G, et al. ERA5-Land: a state-of-the-art global reanalysis dataset for land applications. Earth Syst Sci Data. 2021;13(9):4349–83. doi:10.5194/essd-13-4349-2021.
47. Hersbach H, Bell B, Berrisford P, Hirahara S, Horányi A, Muñoz-Sabater J, et al. The ERA5 global reanalysis. Q J R Meteorol Soc. 2020;146(730):1999–2049. doi:10.1002/qj.3803.
48. Ravshanov N, Abdullaev Z, Shafiyev T. Mathematical model and numerical algorithm to study the process of aerosol particles distribution in the atmosphere. In: 2019 International Conference on Information Science and Communications Technologies (ICISCT); 2019 Nov 4–6; Tashkent, Uzbekistan. Piscataway: IEEE; 2019. doi:10.1109/ICISCT47635.2019.9011878.
49. Shafiev T, Shadmanova G, Karimova K, Muradov F. Nonlinear mathematical model and numerical algorithm for monitoring and predicting the concentration of harmful substances in the atmosphere. E3S Web Conf. 2021;264:01021. doi:10.1051/e3sconf/202126401021.
50. Shafiyev T, Nazarov S. Studies of the influence of vegetation cover on the process of transfer and diffusion of harmful substances in the atmosphere. E3S Web Conf. 2023;431:01059. doi:10.1051/e3sconf/202343101059.
51. Shafiev T. Development of a mathematical model and an efficient computational algorithm for predicting atmospheric pollution in industrial regions. AIP Conf Proc. 2024;3004(1):060005. doi:10.1063/5.0199817.
52. Ravshanov N, Muradov F, Akhmedov D. Operator splitting method for numerical solving the atmospheric pollutant dispersion problem. J Phys Conf Ser. 2020;1441(1):012164. doi:10.1088/1742-6596/1441/1/012164.
53. Crank J, Nicolson P. A practical method for numerical evaluation of solutions of partial differential equations of the heat-conduction type. Math Proc Camb Philos Soc. 1947;43(1):50–67. doi:10.1017/S0305004100023197.
54. Bobojonova MA, Shafiyev TR. DustVel: software for computing the velocities of dust particles in the atmosphere [software]. Zenodo; 2026. doi:10.5281/zenodo.22735087.
55. Samarskii AA. The theory of difference schemes. New York: Marcel Dekker; 2001.
56. Marchuk GI. Splitting methods. Moscow: Nauka; 1988 (In Russian).
57. Yanenko NN. The method of fractional steps. Berlin: Springer; 1971.
58. van Leer B. Towards the ultimate conservative difference scheme. II. Monotonicity and conservation combined in a second-order scheme. J Comput Phys. 1974;14(4):361–70. doi:10.1016/0021-9991(74)90019-9.
59. Poggio L, de Sousa LM, Batjes NH, Heuvelink GBM, Kempen B, Ribeiro E, et al. SoilGrids 2.0: producing soil information for the globe with quantified spatial uncertainty. SOIL. 2021;7(1):217–40. doi:10.5194/soil-7-217-2021.
60. European Space Agency. Copernicus Global Digital Elevation Model (GLO-90) [dataset]. 2021. doi:10.5270/ESA-c5d3d65.
61. Zanaga D, Van De Kerchove R, Daems D, De Keersmaecker W, Brockmann C, Kirches G, et al. ESA WorldCover 10 m 2021 v200 [dataset]. Zenodo; 2022. doi:10.5281/zenodo.7254221.
62. Inness A, Ades M, Agustí-Panareda A, Barré J, Benedictow A, Blechschmidt AM, et al. The CAMS reanalysis of atmospheric composition. Atmos Chem Phys. 2019;19(6):3515–56. doi:10.5194/acp-19-3515-2019.
63. Chang JC, Hanna SR. Air quality model performance evaluation. Meteorol Atmos Phys. 2004;87(1–3):167–96. doi:10.1007/s00703-003-0070-7.
