tic
clear; clc; close all;

% Resolve inputs beside this script; preserve archived figures on every run.
scriptDir = fileparts(mfilename('fullpath'));
outputRoot = getenv('QUANTU_OUTPUT_DIR');
if isempty(outputRoot)
    outputRoot = fullfile(scriptDir, '..', '..', '..', 'results', 'density-matrix');
end
outputDir = fullfile(outputRoot, ['direct_' datestr(now, 'yyyymmddTHHMMSSFFF')]);

%% ============================================================
%  SLOW / DIRECT density-matrix steady-state model for Rb D2 absorption
%  85Rb + 87Rb, hyperfine + Zeeman sublevels F,mF
%
%  Purpose:
%      Diagnostic version to validate the fast Doppler interpolation code.
%
%  Model:
%      d rho/dt = -i[H(Omega,v_z),rho] + L_sp[rho] + L_grel[rho]
%
%  For every pair (Omega_i, Doppler_j), we solve explicitly:
%
%      L(Omega_i,Doppler_j) rho_ss(Omega_i,Doppler_j) = 0,
%      Tr(rho_ss) = 1.
%
%  Then we Doppler-average the absorptive optical coherence:
%
%      alpha(Omega_i) =
%          int dD P(D) Im[ sum_{g,e} d_eg^* rho_ge^ss(Omega_i,D) ].
%
%  Frequency convention:
%      Omega = nu_85_D2_center - nu_L
%
%  Single travelling-wave Doppler convention:
%      x = Omega - Doppler,
%      Doppler = v_z/lambda in MHz.
%
%  Important:
%      This version intentionally avoids the response-grid/interp1
%      acceleration. It still uses the affine Liouvillian
%
%          L(Omega,D) = L0 + (Omega-D)Ldet
%
%      but solves the steady state independently for each pair
%      (Omega_i,D_j).
%
%  Recommended first test:
%      NOmega = 301, Nv = 301.
%
%  Full high-resolution runs:
%      NOmega = 1001, Nv = 2001
%      are very expensive.
% ============================================================

%% ---------------- Numerical controls ----------------
NOmega = 301;          % diagnostic default. Increase after validation.
Nv     = 301;          % diagnostic default. Increase after validation.

Omega_MHz = linspace(-6000, 6000, NOmega);

% Parallel option
useParallel = true;     % falls back to serial if unavailable
if useParallel && ~license('test', 'Distrib_Computing_Toolbox')
    warning('QuAntu:SerialFallback', 'Parallel Computing Toolbox unavailable; using serial CPU.');
    useParallel = false;
end

% Polarization mode:
%   'pi'          : Delta m = 0
%   'sigma_plus'  : Delta m = +1
%   'sigma_minus' : Delta m = -1
%   'linear_x'    : coherent sigma+ + sigma-
polMode = 'linear_x';

% Base resonant Rabi frequency in MHz.
% Small Omega0_MHz -> almost linear absorption.
% Large Omega0_MHz -> saturation + optical pumping.
Omega0_MHz = 10.0;

% Phenomenological ground-state relaxation/mixing rate [MHz].
% Mimics transit relaxation, collisions, magnetic-field mixing, etc.
% It prevents artificial trapping into perfectly dark states.
gamma_g_MHz = 0.05;

% Natural linewidth, D2 line, FWHM in MHz
Gamma_MHz = 6.0666;

% Global optical-depth scale for plotting absorption as 1-exp(-OD)
maxAbsPaper = 0.42;

% Use Beer-Lambert conversion A = 1-exp(-OD)
useBeerLambert = true;

% For this diagnostic, keep false first.
% If true, this only changes the plotted horizontal axis;
% it is NOT inserted into the Hamiltonian.
useAxisCalibration = false;
aCal = 1.0434;
bCal = 0.0781;   % GHz

%% ---------------- Physical constants ----------------
kB  = 1.380649e-23;                 % J/K
amu = 1.66053906660e-27;            % kg
T   = 293;                          % K

%% ---------------- Natural abundances ----------------
eta85 = 0.72;
eta87 = 1 - eta85;

etaTot = eta85 + eta87;
eta85 = eta85 / etaTot;
eta87 = eta87 / etaTot;

%% ---------------- Optical data ----------------
lambda85 = 780.241368271e-9;        % m
lambda87 = 780.241209686e-9;        % m

isoShift_87_minus_85_MHz = 78.095;

%% ---------------- Define isotopes ----------------
rb85 = make_rb85(amu, lambda85);
rb87 = make_rb87(amu, lambda87);

% Paper convention:
%
%   Omega = nu_85_D2_center - nu_L.
%
% Therefore the 85Rb D2 fine center is zero, while the 87Rb
% D2 fine center is +78.095 MHz in optical frequency.
% The sign on the plotted Omega axis is handled in the Hamiltonian.
rb85.isoCenter_MHz = 0.0;
rb87.isoCenter_MHz = isoShift_87_minus_85_MHz;

%% ---------------- Doppler widths ----------------
sigma_v_85 = sqrt(kB*T/rb85.mass);
sigma_v_87 = sqrt(kB*T/rb87.mass);

sigmaD_85 = sigma_v_85 / rb85.lambda / 1e6;      % MHz
sigmaD_87 = sigma_v_87 / rb87.lambda / 1e6;      % MHz

fprintf('============================================================\n');
fprintf('SLOW direct density-matrix Rb D2 absorption model\n');
fprintf('============================================================\n');
fprintf('T = %.1f K\n', T);
fprintf('sigma_D(85Rb) = %.2f MHz\n', sigmaD_85);
fprintf('sigma_D(87Rb) = %.2f MHz\n', sigmaD_87);
fprintf('Omega0 effective = %.2f MHz\n', Omega0_MHz);
fprintf('Ground relaxation = %.3f MHz\n', gamma_g_MHz);
fprintf('Natural abundance ratio 85Rb/87Rb = %.3f\n', eta85/eta87);
fprintf('NOmega = %d, Nv = %d\n', NOmega, Nv);
fprintf('useParallel = %d\n', useParallel);
fprintf('useAxisCalibration = %d\n', useAxisCalibration);
fprintf('useBeerLambert = %d\n', useBeerLambert);

%% ---------------- Direct density-matrix spectra ----------------
% Optional polarization average.
% For the first diagnostic, use false and one controlled polarization.
usePolarizationAverage = false;

if usePolarizationAverage

    polList = {'pi','sigma_plus','sigma_minus'};

    alpha85_all = zeros(numel(polList), numel(Omega_MHz));
    alpha87_all = zeros(numel(polList), numel(Omega_MHz));

    for ip = 1:numel(polList)

        polModeNow = polList{ip};

        fprintf('\n============================================================\n');
        fprintf('Computing polarization component: %s\n', polModeNow);
        fprintf('============================================================\n');

        fprintf('\nComputing 85Rb direct pair-by-pair spectrum...\n');
        alpha85_all(ip,:) = density_matrix_spectrum_direct_pairs( ...
            rb85, Omega_MHz, sigmaD_85, Nv, Gamma_MHz, ...
            Omega0_MHz, gamma_g_MHz, polModeNow, useParallel);

        fprintf('\nComputing 87Rb direct pair-by-pair spectrum...\n');
        alpha87_all(ip,:) = density_matrix_spectrum_direct_pairs( ...
            rb87, Omega_MHz, sigmaD_87, Nv, Gamma_MHz, ...
            Omega0_MHz, gamma_g_MHz, polModeNow, useParallel);
    end

    alpha85 = mean(alpha85_all, 1);
    alpha87 = mean(alpha87_all, 1);

else

    fprintf('\nComputing 85Rb direct pair-by-pair spectrum...\n');
    alpha85 = density_matrix_spectrum_direct_pairs( ...
        rb85, Omega_MHz, sigmaD_85, Nv, Gamma_MHz, ...
        Omega0_MHz, gamma_g_MHz, polMode, useParallel);

    fprintf('\nComputing 87Rb direct pair-by-pair spectrum...\n');
    alpha87 = density_matrix_spectrum_direct_pairs( ...
        rb87, Omega_MHz, sigmaD_87, Nv, Gamma_MHz, ...
        Omega0_MHz, gamma_g_MHz, polMode, useParallel);

end

%% ---------------- Natural mixture ----------------
OD85_raw = eta85 * alpha85;
OD87_raw = eta87 * alpha87;

OD_raw = OD85_raw + OD87_raw;

if max(OD_raw) <= 0
    error('OD_raw has non-positive maximum. Check sign conventions or alpha calculation.');
end

if useBeerLambert

    % Target maximum absorption for comparison with experiment.
    % This fixes only the vertical scale.
    ODmax = -log(1 - maxAbsPaper);

    % Global optical-depth scale.
    scaleOD = ODmax / max(OD_raw);

    OD85 = scaleOD * OD85_raw;
    OD87 = scaleOD * OD87_raw;
    OD_total = OD85 + OD87;

    Abs_total = 1 - exp(-OD_total);

    % Additive plotting decomposition:
    % these are not independent Beer-Lambert absorptions.
    Abs85 = zeros(size(Abs_total));
    Abs87 = zeros(size(Abs_total));

    mask = OD_total > 0;
    Abs85(mask) = Abs_total(mask) .* OD85(mask) ./ OD_total(mask);
    Abs87(mask) = Abs_total(mask) .* OD87(mask) ./ OD_total(mask);

else

    % Linear response approximation: A approximately proportional to OD.
    scaleAbs = maxAbsPaper / max(OD_raw);

    Abs85 = scaleAbs * OD85_raw;
    Abs87 = scaleAbs * OD87_raw;
    Abs_total = Abs85 + Abs87;

end

%% ---------------- Experimental data ----------------
% File examples:
%   DATA_ABS_Rb.csv
%   Data_Rb_Gas.csv
%
% Expected format:
%   column 1: experimental detuning [GHz]
%   column 2: absorption [arb. units]
expFile = fullfile(scriptDir, 'DATA_ABS_Rb.csv');
haveExp = isfile(expFile);

if haveExp
    data_exp = readmatrix(expFile);

    delta_exp_GHz = data_exp(:,1);
    signal_exp    = data_exp(:,2);
else
    warning('Experimental file "%s" not found. Plotting only theory.', expFile);
end

%% ---------------- Frequency axis for plotting ----------------
Omega_theory_GHz = Omega_MHz * 1e-3;

if useAxisCalibration
    Omega_plot_GHz = aCal * Omega_theory_GHz + bCal;
else
    Omega_plot_GHz = Omega_theory_GHz;
end

%% ---------------- Plot ----------------
fig = figure('Color','w');
set(fig, 'Units', 'centimeters', 'Position', [2 2 24 15]);

hold on

plot(Omega_plot_GHz, Abs_total, 'k-', 'LineWidth', 2.8)
plot(Omega_plot_GHz, Abs85, '--', 'LineWidth', 2.0)
plot(Omega_plot_GHz, Abs87, '--', 'LineWidth', 2.0)

if haveExp
    scatter(delta_exp_GHz, signal_exp, 45, 'o', ...
        'filled', ...
        'MarkerFaceAlpha', 0.75, ...
        'MarkerEdgeAlpha', 0.75)
end

hold off
box on

xlabel('$\delta$ (GHz)', 'Interpreter','latex', 'FontSize', 22)
ylabel('Absorption', 'Interpreter','latex', 'FontSize', 22)

set(gca, ...
    'FontSize', 20, ...
    'LineWidth', 1.3, ...
    'TickLabelInterpreter', 'latex')

xlim([-6 6])

if haveExp
    yMax = max([Abs_total(:); signal_exp(:)]);
else
    yMax = max(Abs_total(:));
end
ylim([0 1.12*yMax])

%% ---------------- Legend outside ----------------
if haveExp
    lgd = legend({'Theory direct', ...
                  '${}^{85}$Rb contribution', ...
                  '${}^{87}$Rb contribution', ...
                  'Experiment'}, ...
                  'Interpreter','latex', ...
                  'FontSize', 16, ...
                  'Location','northoutside', ...
                  'Orientation','horizontal');
else
    lgd = legend({'Theory direct', ...
                  '${}^{85}$Rb contribution', ...
                  '${}^{87}$Rb contribution'}, ...
                  'Interpreter','latex', ...
                  'FontSize', 16, ...
                  'Location','northoutside', ...
                  'Orientation','horizontal');
end

lgd.Box = 'off';

ax = gca;
ax.Position = [0.12 0.16 0.82 0.68];

%% ---------------- Save figure ----------------
if ~isfolder(outputDir)
    mkdir(outputDir);
end
savefig(fig, fullfile(outputDir, 'Rb_absorption_spectrum_slow_direct.fig'));

set(fig, 'Renderer', 'painters');
print(fig, fullfile(outputDir, 'Rb_absorption_spectrum_slow_direct.svg'), '-dsvg');
print(fig, fullfile(outputDir, 'Rb_absorption_spectrum_slow_direct.pdf'), '-dpdf', '-bestfit');
print(fig, fullfile(outputDir, 'Rb_absorption_spectrum_slow_direct.png'), '-dpng', '-r300');
fprintf('Figures saved in: %s\n', outputDir);

%% ---------------- Print transition centers ----------------
fprintf('\n============================================================\n');
fprintf('Transition centers on paper axis: Omega = nu_85D2 - nu_L\n');
fprintf('============================================================\n');

print_transition_centers(rb85);
print_transition_centers(rb87);

fprintf('\n============================================================\n');
fprintf('Group-center diagnostic from energy gaps and line strengths\n');
fprintf('============================================================\n');

diagnose_group_centers(rb85);
diagnose_group_centers(rb87);

toc

%% ============================================================
%                         FUNCTIONS
% ============================================================

function alpha = density_matrix_spectrum_direct_pairs(rb, Omega_MHz, sigmaD_MHz, Nv, ...
    Gamma_MHz, Omega0_MHz, gamma_g_MHz, polMode, useParallel)
% ============================================================
% Direct pair-by-pair density-matrix Doppler spectrum.
%
% For every laser detuning Omega_i and every Doppler class D_j,
% this function solves the steady-state master equation
%
%       L(Omega_i,D_j) rho_ss(Omega_i,D_j) = 0,
%       Tr[rho_ss] = 1.
%
% For a single travelling-wave field, the velocity dependence enters as
%
%       x_ij = Omega_i - D_j,
%
% where D_j = v_z/lambda in MHz.
%
% This function intentionally does NOT build a response grid and does
% NOT call interp1. It computes rho_ss separately for every pair.
% ============================================================

states = build_basis(rb);
N = numel(states);

fprintf('%s direct: Hilbert dimension N = %d, Liouville dimension = %d\n', ...
    rb.name, N, N^2);

Dip = build_dipole_operator(rb, states, polMode);

Gamma_rad   = 2*pi*Gamma_MHz;
gamma_g_rad = 2*pi*gamma_g_MHz;

GammaExtraFWHM_MHz = 0;
Ldiss = build_dissipator(rb, states, Gamma_rad, gamma_g_rad, GammaExtraFWHM_MHz);

% Doppler grid in frequency units D = v_z/lambda [MHz]
Doppler = linspace(-4*sigmaD_MHz, 4*sigmaD_MHz, Nv);

P = exp(-Doppler.^2/(2*sigmaD_MHz^2));
P = P / trapz(Doppler, P);

% Affine Liouvillian:
%
%       L(Omega,D) = L0 + (Omega-D)Ldet.
%
% This avoids rebuilding sparse operators from scratch, but still solves
% one independent steady-state problem for every pair (Omega_i,D_j).
[L0, Ldet, b, absVec] = prepare_affine_liouvillian( ...
    rb, states, Dip, Ldiss, Omega0_MHz);

NOmega = numel(Omega_MHz);
alpha = zeros(1, NOmega);

fprintf('%s direct: solving %d x %d = %d steady-state systems\n', ...
    rb.name, NOmega, Nv, NOmega*Nv);

if useParallel
    try
        pool = gcp('nocreate');
        if isempty(pool)
            parpool;
        end
    catch poolError
        warning('QuAntu:SerialFallback', 'Cannot start parallel pool: %s. Using serial CPU.', poolError.message);
        useParallel = false;
    end
end

if useParallel
    parfor iO = 1:NOmega

        OmegaNow = Omega_MHz(iO);
        resp_v = zeros(1, Nv);

        for iv = 1:Nv

            Dnow = Doppler(iv);

            % Pair-dependent effective detuning.
            xPair = OmegaNow - Dnow;

            % Pair-dependent steady-state Liouvillian.
            A = L0 + xPair * Ldet;

            % Solve steady state with trace condition.
            rhoVec = A \ b;

            % Absorptive optical coherence.
            resp_v(iv) = imag(absVec.' * rhoVec);
        end

        % Doppler average for this laser detuning.
        alpha(iO) = trapz(Doppler, resp_v .* P);
    end

else

    for iO = 1:NOmega

        OmegaNow = Omega_MHz(iO);
        resp_v = zeros(1, Nv);

        for iv = 1:Nv

            Dnow = Doppler(iv);
            xPair = OmegaNow - Dnow;

            A = L0 + xPair * Ldet;
            rhoVec = A \ b;

            resp_v(iv) = imag(absVec.' * rhoVec);
        end

        alpha(iO) = trapz(Doppler, resp_v .* P);

        if mod(iO, 10) == 0 || iO == 1 || iO == NOmega
            fprintf('  %s direct: Omega point %d / %d done\n', ...
                rb.name, iO, NOmega);
        end
    end
end

% Robust global sign convention.
if max(alpha) < abs(min(alpha))
    alpha = -alpha;
end

% Clip tiny numerical negatives.
alpha(alpha < 0) = 0;

end

function [L0, Ldet, b, absVec] = prepare_affine_liouvillian( ...
    rb, states, Dip, Ldiss, Omega0_MHz)

N = numel(states);

Hdiag_const_MHz = zeros(N,1);
Hdiag_det_MHz   = zeros(N,1);

for a = 1:N

    if states(a).manifold == 'g'

        Hdiag_const_MHz(a) = states(a).E_MHz;
        Hdiag_det_MHz(a)   = 0;

    else

        % Excited rotating-frame energy:
        %
        %       E_e + isotope shift + x
        %
        % Resonance condition:
        %
        %       x + iso + E_e - E_g = 0.
        %
        % For each pair:
        %
        %       x = Omega - Doppler.
        Hdiag_const_MHz(a) = states(a).E_MHz + rb.isoCenter_MHz;
        Hdiag_det_MHz(a)   = 1;

    end
end

Hconst = spdiags(2*pi*Hdiag_const_MHz, 0, N, N);
Hdet   = spdiags(2*pi*Hdiag_det_MHz,   0, N, N);

Omega0_rad = 2*pi*Omega0_MHz;

% RWA interaction:
%
%       H_int = Omega0/2 * (D + D^\dagger)
%
Hint = 0.5 * Omega0_rad * (Dip + Dip');

Hconst = Hconst + Hint;

L0   = liouvillian_hamiltonian(Hconst) + Ldiss;
Ldet = liouvillian_hamiltonian(Hdet);

% Insert trace condition:
%
%       Tr(rho) = 1
%
traceRow = sparse(1, N^2);

for n = 1:N
    traceRow(1, n + (n-1)*N) = 1;
end

L0(1,:)   = traceRow;
Ldet(1,:) = sparse(1, N^2);

b = zeros(N^2,1);
b(1) = 1;

% Vector that extracts the absorptive optical coherence.
%
% MATLAB vectorization uses idx = row + (col-1)*N.
% The optical coherence rho_ge corresponds to row=g, col=e.
%
% Absorption proxy:
%
%   alpha ~ Im[ sum_{g,e} conj(d_eg) rho_ge ]
%
% where d_eg = Dip(e,g) is the driven dipole matrix element.
absVec = sparse(N^2,1);

for g = 1:N

    if states(g).manifold ~= 'g'
        continue;
    end

    for e = 1:N

        if states(e).manifold ~= 'e'
            continue;
        end

        d_eg = Dip(e,g);

        if abs(d_eg) > 0
            idx_ge = g + (e-1)*N;
            absVec(idx_ge) = conj(d_eg);
        end
    end
end

end

function states = build_basis(rb)

count = 0;
states = struct('manifold',{},'F',{},'m',{},'E_MHz',{},'index',{});

% Ground states
for F = rb.Fg

    Eg = hyperfine_shift_MHz(rb.I, rb.Jg, rb.Ag, rb.Bg, F);

    for m = -F:F

        count = count + 1;
        states(count).manifold = 'g';
        states(count).F = F;
        states(count).m = m;
        states(count).E_MHz = Eg;
        states(count).index = count;

    end
end

% Excited states
for F = rb.Fe

    Ee = hyperfine_shift_MHz(rb.I, rb.Je, rb.Ae, rb.Be, F);

    for m = -F:F

        count = count + 1;
        states(count).manifold = 'e';
        states(count).F = F;
        states(count).m = m;
        states(count).E_MHz = Ee;
        states(count).index = count;

    end
end

end

function Dip = build_dipole_operator(rb, states, polMode)

N = numel(states);
Dip = sparse(N,N);

pol = polarization_components(polMode);

for ig = 1:N

    if states(ig).manifold ~= 'g'
        continue;
    end

    Fg = states(ig).F;
    mg = states(ig).m;

    for ie = 1:N

        if states(ie).manifold ~= 'e'
            continue;
        end

        Fe = states(ie).F;
        me = states(ie).m;

        % qLight = me - mg
        % sigma+ : +1
        % pi     :  0
        % sigma- : -1
        qLight = me - mg;

        if abs(qLight) > 1
            continue;
        end

        epsq = get_pol(pol, qLight);

        if abs(epsq) == 0
            continue;
        end

        amp = dipole_amp_D2(rb.I, rb.Jg, rb.Je, Fg, mg, Fe, me);

        % Dip maps ground -> excited.
        Dip(ie,ig) = epsq * amp;

    end
end

end

function pol = polarization_components(polMode)

% Components indexed by qLight = -1,0,+1
pol.qm = 0;
pol.q0 = 0;
pol.qp = 0;

switch polMode

    case 'pi'
        pol.q0 = 1;

    case 'sigma_plus'
        pol.qp = 1;

    case 'sigma_minus'
        pol.qm = 1;

    case 'linear_x'
        % Linear polarization perpendicular to quantization axis:
        % coherent sigma+ + sigma- superposition.
        pol.qp = 1/sqrt(2);
        pol.qm = 1/sqrt(2);

    otherwise
        error('Unknown polarization mode: %s', polMode);
end

end

function epsq = get_pol(pol, qLight)

if qLight == -1
    epsq = pol.qm;
elseif qLight == 0
    epsq = pol.q0;
elseif qLight == 1
    epsq = pol.qp;
else
    epsq = 0;
end

end

function amp = dipole_amp_D2(I, Jg, Je, Fg, mg, Fe, me)
% Dimensionless dipole matrix element in units of
%
%       <Jg=1/2 || er || Je=3/2>.
%
% Selection rule in the 3j symbol uses q = mg - me.

q = mg - me;

if abs(q) > 1
    amp = 0;
    return;
end

if abs(me) > Fe || abs(mg) > Fg
    amp = 0;
    return;
end

w6 = wigner6j_racah(Jg, Je, 1, Fe, Fg, I);
w3 = wigner3j_racah(Fe, 1, Fg, me, q, -mg);

phasePower = round(Fe - 1 + mg);
phase = (-1)^phasePower;

amp = phase * sqrt((2*Fg+1)*(2*Fe+1)*(2*Jg+1)) * w6 * w3;

end

function Ldiss = build_dissipator(rb, states, Gamma_rad, gamma_g_rad, GammaExtraFWHM_MHz)

N = numel(states);
Ldiss = sparse(N^2,N^2);

% ---------------- Spontaneous emission ----------------
eList = find(arrayfun(@(s) s.manifold == 'e', states));
gList = find(arrayfun(@(s) s.manifold == 'g', states));

for ee = eList

    weights = zeros(size(gList));

    Fe = states(ee).F;
    me = states(ee).m;

    for kk = 1:numel(gList)

        gg = gList(kk);

        Fg = states(gg).F;
        mg = states(gg).m;

        amp = dipole_amp_D2(rb.I, rb.Jg, rb.Je, Fg, mg, Fe, me);
        weights(kk) = abs(amp)^2;

    end

    sw = sum(weights);

    if sw > 0
        weights = weights / sw;
    end

    for kk = 1:numel(gList)

        if weights(kk) <= 0
            continue;
        end

        gg = gList(kk);

        C = sparse(N,N);
        C(gg,ee) = sqrt(Gamma_rad * weights(kk));

        Ldiss = Ldiss + lindblad_superoperator(C);

    end
end

% ---------------- Ground-state relaxation / mixing ----------------
% Thermal repopulation uniformly over all ground Zeeman sublevels.
% This phenomenological channel prevents accumulation in perfectly
% dark states and mimics transit-time / collisional remixing.

Ng = numel(gList);
pTarget = ones(Ng,1) / Ng;

if gamma_g_rad > 0

    for ii = 1:Ng

        gi = gList(ii);

        for jj = 1:Ng

            gj = gList(jj);

            C = sparse(N,N);
            C(gj,gi) = sqrt(gamma_g_rad * pTarget(jj));

            Ldiss = Ldiss + lindblad_superoperator(C);

        end
    end
end

% ---------------- Extra optical dephasing ----------------
% GammaExtraFWHM_MHz is an additional homogeneous optical linewidth.
% It damps optical coherences without changing populations directly.

gammaOpt_rad = 2*pi*GammaExtraFWHM_MHz;

if gammaOpt_rad > 0

    for ee = eList

        C = sparse(N,N);
        C(ee,ee) = sqrt(gammaOpt_rad);

        Ldiss = Ldiss + lindblad_superoperator(C);

    end
end

end

function L = liouvillian_hamiltonian(H)

N = size(H,1);
Iden = speye(N);

% vec(H rho - rho H) = (I kron H - H^T kron I) vec(rho)
L = -1i * (kron(Iden,H) - kron(transpose(H),Iden));

end

function Lc = lindblad_superoperator(C)

N = size(C,1);
Iden = speye(N);
CdC = C' * C;

Lc = kron(conj(C), C) ...
    - 0.5 * kron(Iden, CdC) ...
    - 0.5 * kron(transpose(CdC), Iden);

end

function rb = make_rb85(amu, lambda)

rb.name = '85Rb';
rb.isotope = 85;

rb.I  = 5/2;
rb.Jg = 1/2;
rb.Je = 3/2;

rb.Fg = [2 3];
rb.Fe = [1 2 3 4];

% Hyperfine constants in MHz
rb.Ag = 1011.9108130;      % 5^2S_{1/2}
rb.Bg = 0;
rb.Ae = 25.0354;           % 5^2P_{3/2}
rb.Be = 25.898;            % 5^2P_{3/2}

rb.mass = 84.911789732 * amu;
rb.lambda = lambda;

end

function rb = make_rb87(amu, lambda)

rb.name = '87Rb';
rb.isotope = 87;

rb.I  = 3/2;
rb.Jg = 1/2;
rb.Je = 3/2;

rb.Fg = [1 2];
rb.Fe = [0 1 2 3];

% Hyperfine constants in MHz
rb.Ag = 3417.341305452145; % 5^2S_{1/2}
rb.Bg = 0.0;
rb.Ae = 84.7185;           % 5^2P_{3/2}
rb.Be = 12.4965;           % 5^2P_{3/2}

rb.mass = 86.909180520 * amu;
rb.lambda = lambda;

end

function dE = hyperfine_shift_MHz(I,J,A,B,F)
% Hyperfine energy shift DeltaE/h in MHz.
%
% K = F(F+1) - I(I+1) - J(J+1)
%
% DeltaE/h =
%   (1/2) A K
%   + B * [(3/2)K(K+1) - 2I(I+1)J(J+1)]
%       / [4I(2I-1)J(2J-1)]

K = F*(F+1) - I*(I+1) - J*(J+1);

dE = 0.5 * A * K;

if (I > 0.5) && (J > 0.5) && (B ~= 0)

    num = (3/2)*K*(K+1) - 2*I*(I+1)*J*(J+1);
    den = 4*I*(2*I-1)*J*(2*J-1);

    dE = dE + B * num / den;

end

end

function print_transition_centers(rb)

fprintf('\n--- %s ---\n', rb.name);

for Fg = rb.Fg

    Eg = hyperfine_shift_MHz(rb.I, rb.Jg, rb.Ag, rb.Bg, Fg);

    for Fe = rb.Fe

        if abs(Fe-Fg) <= 1 && ~(Fe==0 && Fg==0)

            Ee = hyperfine_shift_MHz(rb.I, rb.Je, rb.Ae, rb.Be, Fe);

            % Optical transition frequency relative to 85Rb D2 center.
            nuRel_MHz = rb.isoCenter_MHz + Ee - Eg;

            % Paper/theory axis:
            %
            %       Omega = nu_85D2 - nu_L.
            OmegaCenter_MHz = -nuRel_MHz;

            fprintf('%s F=%g -> F''=%g : Omega = %+9.3f MHz\n', ...
                rb.name, Fg, Fe, OmegaCenter_MHz);

        end
    end
end

end

function diagnose_group_centers(rb)

fprintf('\n--- %s ---\n', rb.name);

for Fg = rb.Fg

    Eg = hyperfine_shift_MHz(rb.I, rb.Jg, rb.Ag, rb.Bg, Fg);

    centers = [];
    weights = [];

    fprintf('\nGround manifold F=%g\n', Fg);

    for Fe = rb.Fe

        if abs(Fe-Fg) <= 1 && ~(Fe==0 && Fg==0)

            Ee = hyperfine_shift_MHz(rb.I, rb.Je, rb.Ae, rb.Be, Fe);

            % Theory axis: Omega = nu_85D2 - nu_L.
            center_MHz = -(rb.isoCenter_MHz + Ee - Eg);

            S = relative_strength_steck_D2(rb.isotope, Fg, Fe);

            centers(end+1) = center_MHz; %#ok<AGROW>
            weights(end+1) = S;          %#ok<AGROW>

            fprintf('  F=%g -> F''=%g : Omega = %+9.3f MHz, S = %.5f\n', ...
                Fg, Fe, center_MHz, S);

        end
    end

    cWeighted = sum(weights .* centers) / sum(weights);

    fprintf('  Weighted center for %s F=%g group: %+9.3f MHz = %+7.4f GHz\n', ...
        rb.name, Fg, cWeighted, cWeighted*1e-3);

end

end

function S = relative_strength_steck_D2(isotope, Fg, Fe)
% Relative hyperfine transition strengths S_FF' for Rb D2.
% Values from Steck tables.

S = 0;

if isotope == 85

    if Fg == 2 && Fe == 1
        S = 3/10;
    elseif Fg == 2 && Fe == 2
        S = 7/18;
    elseif Fg == 2 && Fe == 3
        S = 14/45;
    elseif Fg == 3 && Fe == 2
        S = 5/63;
    elseif Fg == 3 && Fe == 3
        S = 5/18;
    elseif Fg == 3 && Fe == 4
        S = 9/14;
    end

elseif isotope == 87

    if Fg == 1 && Fe == 0
        S = 1/6;
    elseif Fg == 1 && Fe == 1
        S = 5/12;
    elseif Fg == 1 && Fe == 2
        S = 5/12;
    elseif Fg == 2 && Fe == 1
        S = 1/20;
    elseif Fg == 2 && Fe == 2
        S = 1/4;
    elseif Fg == 2 && Fe == 3
        S = 7/10;
    end

end

end

%% ============================================================
%                Wigner 3j and 6j implementations
% ============================================================

function val = wigner3j_racah(j1,j2,j3,m1,m2,m3)
% Wigner 3j symbol using Racah formula.

if abs(m1 + m2 + m3) > 1e-12
    val = 0;
    return;
end

if abs(m1) > j1 || abs(m2) > j2 || abs(m3) > j3
    val = 0;
    return;
end

if ~triangle(j1,j2,j3)
    val = 0;
    return;
end

prefPhase = (-1)^round(j1 - j2 - m3);

tri = gamma(j1+j2-j3+1) * gamma(j1-j2+j3+1) * ...
      gamma(-j1+j2+j3+1) / gamma(j1+j2+j3+2);

norm = gamma(j1+m1+1) * gamma(j1-m1+1) * ...
       gamma(j2+m2+1) * gamma(j2-m2+1) * ...
       gamma(j3+m3+1) * gamma(j3-m3+1);

pref = prefPhase * sqrt(tri * norm);

zmin = max([0, j2-j3-m1, j1-j3+m2]);
zmax = min([j1+j2-j3, j1-m1, j2+m2]);

zmin = ceil(zmin - 1e-12);
zmax = floor(zmax + 1e-12);

s = 0;

for z = zmin:zmax

    denom = gamma(z+1) * ...
        gamma(j1+j2-j3-z+1) * ...
        gamma(j1-m1-z+1) * ...
        gamma(j2+m2-z+1) * ...
        gamma(j3-j2+m1+z+1) * ...
        gamma(j3-j1-m2+z+1);

    s = s + (-1)^z / denom;

end

val = pref * s;

end

function val = wigner6j_racah(a,b,c,d,e,f)
% Wigner 6j symbol using Racah formula.

if ~triangle(a,b,c) || ~triangle(a,e,f) || ...
   ~triangle(d,b,f) || ~triangle(d,e,c)

    val = 0;
    return;

end

pref = delta_tri(a,b,c) * delta_tri(a,e,f) * ...
       delta_tri(d,b,f) * delta_tri(d,e,c);

zmin = max([a+b+c, a+e+f, d+b+f, d+e+c]);
zmax = min([a+b+d+e, a+c+d+f, b+c+e+f]);

zmin = ceil(zmin - 1e-12);
zmax = floor(zmax + 1e-12);

s = 0;

for z = zmin:zmax

    denom = gamma(z-a-b-c+1) * ...
        gamma(z-a-e-f+1) * ...
        gamma(z-d-b-f+1) * ...
        gamma(z-d-e-c+1) * ...
        gamma(a+b+d+e-z+1) * ...
        gamma(a+c+d+f-z+1) * ...
        gamma(b+c+e+f-z+1);

    s = s + (-1)^z * gamma(z+2) / denom;

end

val = pref * s;

end

function tf = triangle(a,b,c)

tf = (abs(a-b) <= c + 1e-12) && ...
     (c <= a+b + 1e-12) && ...
     is_int_like(a+b+c);

end

function d = delta_tri(a,b,c)

d = sqrt( gamma(a+b-c+1) * ...
          gamma(a-b+c+1) * ...
          gamma(-a+b+c+1) / ...
          gamma(a+b+c+2) );

end

function tf = is_int_like(x)

tf = abs(x - round(x)) < 1e-12;

end
