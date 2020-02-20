%gdalwarp -tr 30 30 -t_srs epsg:32646 -r bilinear -co COMPRESS=DEFLATE -co ZLEVEL=9 demLat_N28_N34_Lon_E075_E082.dem.nc demLat_N28_N34_Lon_E075_E082.UTM46N.WGS84.tif
addpath(genpath('/home/bodo/topotoolbox'))
rmpath(genpath('/home/bodo/topotoolbox\.git'));

%% Load a DEM
dem_fname="TonsYamuna_SRTM1_30m_UTM46N.tif";
NWHim_dem = GRIDobj(dem_fname);
%imagesc(NWHim_dem)
imageschs(NWHim_dem, NWHim_dem)

NWHim_dem_FIL = fillsinks(NWHim_dem);
NWHim_FD = FLOWobj(NWHim_dem_FIL,'preprocess','carve');
NWHim_FAC = flowacc(NWHim_FD);
figure
imageschs(NWHim_dem, log10(NWHim_FAC))
colorbar
title('Drainage Area (log10)');

dem_resolution = NWHim_dem.refmat(2,1);

% get the DEM resolution, used to convert area threshold to meters squared
area_threshold = 1e6
minApix = area_threshold/(dem_resolution*dem_resolution);
minApix = ceil(minApix);  % convert area threshold to meters specified above

NWHim_FAC_w = NWHim_FAC > minApix;  % masks flow accum grid (above threshold)

NWHim_rivers_w = NWHim_FAC.*(NWHim_FAC.cellsize.^2) > ...
    area_threshold;
NWHim_STR_w = STREAMobj(NWHim_FD, NWHim_FAC_w);
NWHim_rivers_STR = STREAMobj(NWHim_FD, NWHim_rivers_w);

%% extract largest catchment and plot
NWHim_rivers_STR = klargestconncomps(NWHim_rivers_STR, 1);
figure
clf
subplot(2,1,1)
imageschs(NWHim_dem, NWHim_dem, ...
    'ticklabels','nice','colorbar',true)
ylabel('UTM-Northing (m)', 'Fontsize', 12);
xlabel('UTM-Easting (m)', 'Fontsize', 12);
hold on
plot(NWHim_rivers_STR, 'k')
title('Tons-Yamuna River')
subplot(2,1,2)
plotdz(NWHim_rivers_STR, NWHim_dem, 'color', 'k', 'linewidth', 0.5)
hold on
plotdz(trunk(NWHim_rivers_STR),NWHim_dem, 'color', 'b', 'linewidth', 3)

%%
[NWHim_dbasins, NWHim_dbasins_outlet] = drainagebasins(NWHim_FD, NWHim_rivers_STR);
%tons_catchment=-964626.971,3476597.7401
[tons_x, tons_y] = snap2stream(NWHim_rivers_STR,-964626.971,3476597.7401)
[tons_dbasins, tons_dbasins_outlet] = ...
    drainagebasins(NWHim_FD, tons_x, tons_y);
tons_dbasins.Z = logical(tons_dbasins.Z)
Tons_river_mask = and(NWHim_rivers_w, tons_dbasins);

%mask out Tons basin:
Tons_rivers_STR = STREAMobj(NWHim_FD, Tons_river_mask);

%replot only Tons
figure
clf
subplot(2,1,1)
imageschs(NWHim_dem, NWHim_dem, ...
    'ticklabels','nice','colorbar',true)
ylabel('UTM-Northing (m)', 'Fontsize', 12);
xlabel('UTM-Easting (m)', 'Fontsize', 12);
hold on
plot(Tons_rivers_STR, 'k')
title('Tons River')
subplot(2,1,2)
plotdz(Tons_rivers_STR, NWHim_dem, 'color', 'k', 'linewidth', 0.5)
hold on
plotdz(trunk(Tons_rivers_STR),NWHim_dem, 'color', 'b', 'linewidth', 3)

%% calculate slope and area from DEM
% set a minimum gradient (no place in DEM has a slope of 0)
min_str_gradient = 5e-3;
NWHim_mg = imposemin(NWHim_FD, NWHim_dem, min_str_gradient);

NWHim_rivers_slope = gradient(NWHim_rivers_STR,NWHim_mg,'unit','tangent');
NWHim_rivers_area = NWHim_FAC.Z(NWHim_rivers_STR.IXgrid).*...
    (NWHim_FAC.cellsize).^2;
NWHim_rivers_slope_5eminus3 = ...
    find(NWHim_rivers_slope < 4e-3);
NWHim_rivers_slope(NWHim_rivers_slope_5eminus3) = [];
NWHim_rivers_area(NWHim_rivers_slope_5eminus3) = [];

%use slopearea function

%calculate area-slope relation for entire area (may not be useful)
NWHim_slopearea = ...
    slopearea(NWHim_rivers_STR, NWHim_mg,...
    NWHim_FAC, ...
    'areabinlocs', 'median', ...
    'gradaggfun', 'median', ...
    'streamgradient', 'robust', ...
    'mingradient', 1e-2, ...
    'plot', false, ...
    'areabins', 50);

%% Figures
figure;
subplot(1,2,1)
loglog(NWHim_rivers_area, NWHim_rivers_slope, ...
    '.', 'color', [0.8 0.8 0.8])
xlabel('Drainage Area [m^2]')
ylabel('Slope [m/m]')
grid on
hold on
loglog(NWHim_slopearea.a, ...
    NWHim_slopearea.g, ...
    'ks', 'markersize' ,5)
aeval = logspace(log10(min(NWHim_slopearea.a)),log10(max(NWHim_slopearea.a)),10);
geval = NWHim_slopearea.ks(1)*aeval.^NWHim_slopearea.theta;
loglog(aeval, geval, 'k-', 'linewidth', 2)
title(['Yons-Tamuna all data, \theta=',num2str(NWHim_slopearea.theta,2),' and ks=',num2str(NWHim_slopearea.ks,3)])

subplot(1,2,2)
loglog(NWHim_rivers_area, ...
    NWHim_rivers_slope, '.', ...
    'color', [0.8 0.8 0.8])
xlabel('Drainage Area [m^2]')
ylabel('Slope [m/m]')
grid on
hold on
NWHim_slopearea = ...
    slopearea(NWHim_rivers_STR, NWHim_mg,...
    NWHim_FAC, ...
    'areabinlocs', 'median', ...
    'gradaggfun', 'median', ...
    'streamgradient', 'robust', ...
    'hist2', false, ...
    'mingradient', 1e-2, ...
    'plot', false, ...
    'areabins', 50, ...
    'theta', 0.45);
loglog(NWHim_slopearea.a, ...
    NWHim_slopearea.g, ...
    'ks', 'markersize' ,5)

% more flexible fitting of regression
% [beta,R,J,CovB,MSE,ErrorModelInfo] = ...
%     nlinfit(NWHim_slopearea.a,NWHim_slopearea.g,@(b,x) ...
%     b(1)*x.^b(2),[NWHim_slopearea.ks NWHim_slopearea.theta]);
%
%or use a graphical interface:
%nlintool(NWHim_slopearea.a,NWHim_slopearea.g,@(b,x) b(1)*x.^b(2),[NWHim_slopearea.ks NWHim_slopearea.theta],0.05,...
%                 'area','gradient')
aeval = logspace(log10(min(NWHim_slopearea.a)),log10(max(NWHim_slopearea.a)),10);
geval = NWHim_slopearea.ks(1)*aeval.^NWHim_slopearea.theta;
loglog(aeval, geval, 'k-', 'linewidth', 2)
title(['Yons-Tamuna all data, \theta=',num2str(NWHim_slopearea.theta,2),' and ks=',num2str(NWHim_slopearea.ks,3)])

%% Steepness index for Tons River

Tons_rivers_slope = gradient(Tons_rivers_STR,NWHim_mg,'unit','tangent');
Tons_rivers_area = NWHim_FAC.Z(Tons_rivers_STR.IXgrid).*...
    (NWHim_FAC.cellsize).^2;
Tons_rivers_slope_5eminus3 = ...
    find(Tons_rivers_slope < 4e-3);
Tons_rivers_slope(Tons_rivers_slope_5eminus3) = [];
Tons_rivers_area(Tons_rivers_slope_5eminus3) = [];

%use slopearea function

%calculate area-slope relation for entire area (may not be useful)
Tons_slopearea = ...
    slopearea(Tons_rivers_STR, NWHim_mg,...
    NWHim_FAC, ...
    'areabinlocs', 'median', ...
    'gradaggfun', 'median', ...
    'streamgradient', 'robust', ...
    'mingradient', 1e-2, ...
    'plot', false, ...
    'areabins', 50);
figure;
loglog(Tons_rivers_area, Tons_rivers_slope, ...
    '.', 'color', [0.8 0.8 0.8])
xlabel('Drainage Area [m^2]')
ylabel('Slope [m/m]')
grid on
hold on
loglog(Tons_slopearea.a, ...
    Tons_slopearea.g, ...
    'ks', 'markersize' ,5)
aeval = logspace(log10(min(Tons_slopearea.a)),log10(max(Tons_slopearea.a)),10);
geval = Tons_slopearea.ks(1)*aeval.^Tons_slopearea.theta;
loglog(aeval, geval, 'k-', 'linewidth', 2)
title(['Tons-Parbati data, \theta=',num2str(Tons_slopearea.theta,2),' and ks=',num2str(Tons_slopearea.ks,3)])

%% Generate a map of steepness indices
NWHim_slopearea = ...
    slopearea(NWHim_rivers_STR, NWHim_mg,...
    NWHim_FAC, ...
    'areabinlocs', 'median', ...
    'gradaggfun', 'median', ...
    'streamgradient', 'robust', ...
    'mingradient', 1e-2, ...
    'plot', false, ...
    'areabins', 50);

g   = gradient(NWHim_rivers_STR, NWHim_dem);
a   = getnal(NWHim_rivers_STR, NWHim_FAC)*NWHim_FAC.cellsize^2;
NWHim_ksn = g./(a.^NWHim_slopearea.theta);

NWHim_ksna = aggregate(NWHim_rivers_STR,...
    NWHim_ksn,'seglength',1000);

figure
imageschs(NWHim_dem,[],...
    'ticklabels','nice', ...
    'colormap',[.8 .8 .8],...
    'colorbar',false);
hold on 
plotc(NWHim_rivers_STR, NWHim_ksna, ...
    'linewidth', 2)
caxis([0 300])
h   = colorbar;
colormap(jet)
h.Label.String = 'KSn';
box on
axis image

%% Chiplot
c = chiplot(Tons_rivers_STR,NWHim_dem,...
    NWHim_FAC,...
    'mnplot', false, ...
    'fitto', 'ts', ...
    'trunkstream', trunk(Tons_rivers_STR), ...
    'a0', 1e6);
