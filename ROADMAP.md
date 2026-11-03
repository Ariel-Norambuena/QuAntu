# Scientific roadmap

This roadmap covers the components currently versioned in QuAntü (ATE250066). The project brings together Algorithms, Experimental, and Theory groups; the tasks below come from reviewing the report and available models and data. They remain pending unless the validation documentation records evidence of execution.

| Priority | Milestone | Completion criterion |
| --- | --- | --- |
| High | MATLAB–Python parity | Compare observables using identical parameters, grids, and tolerances; record discrepancies and computational cost |
| High | D2 convergence | Sweep spectral, Doppler, and interpolation grids with justified tolerances |
| High | Steady-state validation | Check Liouvillian residual, trace, Hermiticity, and positivity for each isotope and regime |
| High | Fast/direct comparison | Use a common detuning and parameter set, with documented errors and timings |
| High | Data pipeline | Provide an executable transformation from each raw dataset to its processed version, including units and provenance |
| Medium | Common fit evaluation | Evaluate all models on the same data with consistent uncertainty treatment |
| Medium | Absolute calibration | Physically calibrate vapor density, cell length, dipole, and optical field |
| Medium | Magnetic extension | Document the Zeeman Hamiltonian, field, and quantization-axis definition |
| Medium | Reproducible environment | Freeze dependencies after validating each component's full workflow |
| Medium | Citable versions | Agree on authorship, component licenses, and a stable version before publishing a release |

The MOT animation and Qiskit circuits are educational resources. Their illustrations and simulations do not establish that a project experiment has been built or operated.
