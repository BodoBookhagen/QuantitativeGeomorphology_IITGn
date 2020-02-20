%% First steps with topotools
%Download most recent version of topotools from github: https://github.com/wschwanghart/topotoolbox
%on Linux systems, you can do: 
%git clone https://github.com/wschwanghart/topotoolbox

%Make sure to add the correct path to where you have downloaded and
%unzipped topotools:
addpath(genpath('/home/bodo/topotoolbox'))
rmpath(genpath('/home/bodo/topotoolbox\.git'));
%%
%For a detailed introduction to the stream channel theory and chi values, 
%see Neely et al., 2017 (PDF in Matlab-Topotools/Neely17_KZPicker_SCI.pdf) 
%and github repository: https://github.com/UP-RS-ESP/DEM-KZP

%% Load a DEM
dem_fname="Pozo_USGS_UTM11_NAD83_cl2_DEM_1m.tif";
SCI_dem = GRIDobj(dem_fname);
%imagesc(SCI_dem)
imageschs(SCI_dem, SCI_dem)

SCI_dem_FIL = fillsinks(SCI_dem)
SCI_FD = FLOWobj(SCI_dem_FIL,'preprocess','carve');
SCI_FAC = flowacc(SCI_FD);
%dem_FAC_fname="Pozo_USGS_UTM11_NAD83_all_color_cl2_DEM_1m_FAC.tif";
%GRIDobj2geotiff(SCI_FAC,DEM_FAC_fname);

dem_resolution = SCI_dem.refmat(2,1);

% get the DEM resolution, used to convert area threshold to meters squared
area_threshold = 1e4
minApix = area_threshold/(dem_resolution*dem_resolution);
minApix = ceil(minApix);  % convert area threshold to meters specified above

SCI_FAC_w = SCI_FAC > minApix;  % masks flow accum grid (above threshold)

min_drainage_area_to_process = 1e4;
SCI_rivers_w = SCI_FAC.*(SCI_FAC.cellsize.^2) > ...
    min_drainage_area_to_process;
SCI_STR_w = STREAMobj(SCI_FD, SCI_FAC_w);
SCI_rivers_STR = STREAMobj(SCI_FD, SCI_rivers_w);

%extract largest catchment
SCI_rivers_STR = klargestconncomps(SCI_rivers_STR, 1);
figure(1)
imageschs(SCI_dem, SCI_dem, ...
    'ticklabels','nice','colorbar',true)
ylabel('UTM-Northing (m)', 'Fontsize', 12);
xlabel('UTM-Easting (m)', 'Fontsize', 12);
hold on
plot(SCI_rivers_STR, 'k')
plot
[SCI_dbasins, SCI_dbasins_outlet] = drainagebasins(SCI_FD);

%Plot longitudinal river profile
plotdz(SCI_rivers_STR,SCI_dem, 'color', 'k', 'linewidth', 0.5)
hold on
plotdz(trunk(SCI_rivers_STR),SCI_dem, 'color', 'b', 'linewidth', 3)

%calculatuate relief
SCI_DEM_rel_200m = localtopography(SCI_dem, 200);
GRIDobj2geotiff(SCI_DEM_rel_200m,'filename2save.tif');

% calculate slope and area from DEM
% set a minimum gradient (no place in DEM has a slope of 0)
min_str_gradient = 0.0001
SCI_mg = imposemin(SCI_FD,SCI_dem,min_str_gradient);

SCI_rivers_slope = gradient(SCI_rivers_STR,SCI_mg,'unit','tangent');
SCI_rivers_area = SCI_FAC.Z(SCI_rivers_STR.IXgrid).*...
    (SCI_FAC.cellsize).^2;

figure;
loglog(SCI_rivers_area, SCI_rivers_slope, '+')
xlabel('Drainage Area [m^2]')
ylabel('Slope [m/m]')
grid on

%Better approach:
theta=-0.45
SCI_ksn045 = SCI_FAC;
SCI_ksn045 = SCI_dem_gradient8 ./ (SCI_FAC.*...
    (SCI_FAC.cellsize^2)).^theta;
SCI_ksn045.name = 'ksn045';
SCI_ksn045.zunit = 'm^0.9';
%calculate area-slope relation for entire area (may not be useful)
SCI_slopearea = slopearea(SCI_rivers_STR,SCI_mg,...
    SCI_FAC, 'areabinlocs', 'median', 'gradaggfun', 'median', ...
    'streamgradient', 'robust', 'plot', false);

%% Figures
figure;
loglog(SCI_rivers_area, SCI_rivers_slope, '.', 'color', [0.9 0.9 0.9])
xlabel('Drainage Area [m^2]')
ylabel('Slope [m/m]')
grid on
hold on
loglog(SCI_slopearea.a, SCI_slopearea.g, 'ks', 'markersize' ,5)
aeval = logspace(log10(min(SCI_slopearea.a)),log10(max(SCI_slopearea.a)),10);
geval = SCI_slopearea.ks(1)*aeval.^SCI_slopearea.theta;
loglog(aeval, geval, 'k-', 'linewidth', 2)

figure;
loglog(SCI_rivers_area, SCI_rivers_slope, '.', 'color', [0.9 0.9 0.9])
xlabel('Drainage Area [m^2]')
ylabel('Slope [m/m]')
grid on
hold on
SCI_slopearea = slopearea(SCI_rivers_STR,SCI_mg,...
    SCI_FAC, 'areabinlocs', 'median', 'gradaggfun', 'median', ...
    'streamgradient', 'robust', 'plot', false, ...
    'theta', 0.45);
loglog(SCI_slopearea.a, SCI_slopearea.g, 'ks', 'markersize' ,5)
aeval = logspace(log10(min(SCI_slopearea.a)),log10(max(SCI_slopearea.a)),10);
geval = SCI_slopearea.ks(1)*aeval.^SCI_slopearea.theta;
loglog(aeval, geval, 'k-', 'linewidth', 2)

%% Generate a map of steepness indices
g   = gradient(SCI_rivers_STR,SCI_dem);
a   = getnal(SCI_rivers_STR,SCI_FAC)*SCI_FAC.cellsize^2;
SCI_ksn = g./(a.^SCI_slopearea.theta);

%% Map view:
figure;
plotc(SCI_rivers_STR,SCI_ksn)
colormap(jet)
caxis([0 50])
h   = colorbar;
h.Label.String = 'KSn';
box on
axis image

%% aggregate into larger segments 
figure;
SCI_ksna = aggregate(SCI_rivers_STR,SCI_ksn,'seglength',100);
plotc(SCI_rivers_STR,SCI_ksna)
caxis([0 50])
h   = colorbar;
colormap(jet)
h.Label.String = 'KSn';
box on
axis image

%% smooth steepness indices
SCI_ksnsmooth = smooth(SCI_rivers_STR,SCI_ksn);
plotc(SCI_rivers_STR,SCI_ksnsmooth)
caxis([0 50])
h   = colorbar;
colormap(jet)
h.Label.String = 'KSn';
box on
axis image

%% Export as shapefile
S = STREAMobj2mapstruct(SCI_rivers_STR,'seglength',50,'attributes',...
    {'ksn' SCI_ksnsmooth @mean ...
     'uparea' a @mean ...
     'gradient' g @mean});
shapewrite(S,'ksn_testshape.shp');

%% CHIPLOT
c = chiplot(SCI_rivers_STR,SCI_dem,SCI_FAC)

%% MORE FANCY STUFF for plotting
symbolspec_ksn045 = makesymbolspec('line',...
    {'ksn045' [prctile([AOI_STR_MS.ksn045], 5) ...
    prctile([AOI_STR_MS.ksn045], 95)] 'color' jet(6)});
symbolspec_ksnadj = makesymbolspec('line',...
    {'ksnadj' [prctile([AOI_STR_MS.ksnadj], 5) ...
    prctile([AOI_STR_MS.ksnadj], 95)] 'color' jet(6)});
clf
set(gcf,'units','normalized','position',[0 0 1 1]);
set(gcf, 'PaperOrientation', 'landscape');
set(gcf, 'PaperType', PaperType_size);
subplot(2,1,1,'align')
imageschs(AOI_DEM, AOI_DEM, 'caxis', ...
    [floor(min(AOI_DEM(:))) ceil(max(AOI_DEM(:)))], ...
    'colormap',gray,'colorbar',false)
hold on
mapshow(AOI_STR_MS,'SymbolSpec',symbolspec_ksn045, 'Linewidth', 2);
ylabel('UTM-Northing (m)', 'Fontsize', 12);
xlabel('UTM-Easting (m)', 'Fontsize', 12);
title_string = sprintf('%s: K_{sn} -0.45 ', DEM_basename_no_underscore);
title(title_string, 'Fontsize', 14), grid;
colorbar
caxis([prctile([AOI_STR_MS.ksn045], 5) prctile([AOI_STR_MS.ksn045], 95)])
hold off


%save a processed DEM to a geotiff:
%GRIDobj2geotiff(dem_fname);
