#INITIALISE VAIRABLES
# The paths are for inside the container.
# Things will be mounted to /tmp/rackn
$offlineDepots = @(
    "C:/Users/errr/projects/vmware_tools/grd/olb/drpy-agent.zip",
    "C:/Users/errr/projects/vmware_tools/grd/olb/drpy-firewall.zip",
    "C:/Users/errr/projects/vmware_tools/grd/olb/VMware-ESXi-7.0.0-15843807-depot.zip"
)
$imgprofilename  = "RackN-Agent-Enabled-ISO-7.0GA"

#OPTIONS
$withtools = $false #use profile with VMtools or not
$exportiso = $true #export iso
$securityonly = $false #security only profiles
$exportpath = "C:/Users/errr/projects/vmware_tools/grd"

#SCRIPT
#clean the decks
Get-EsxSoftwareDepot | Remove-EsxSoftwareDepot
#add the depot
ForEach($offlineDepot in $offlineDepots)
{
    Add-EsxSoftwareDepot $offlineDepot
}
#view available images in added depots and select the appropriate one
$baseprofile = Get-EsxImageProfile | select * | Out-GridView -PassThru
#create the image profile
#this is a grouping of all the vibs for the install
#clone a profile from the vendor image as a base to work from
New-EsxImageProfile -CloneProfile $baseprofile.Name -Name $imgprofilename -Vendor $baseprofile.vendor -AcceptanceLevel CommunitySupported
#add in the DRPY Agent
Add-EsxSoftwarePackage -ImageProfile $imgprofilename -SoftwarePackage DRP-Firewall-Rule -Force
Add-EsxSoftwarePackage -ImageProfile $imgprofilename -SoftwarePackage DRP-Agent -Force

if ($withtools -eq $true) {
    $toolsFilter = "-standard"
}
else {
    $toolsFilter ="-no-tools"
}

if ($securityonly -eq $false) {
    $securityFilter = "[^s]-(\D*)$"
}

else {
    $securityFilter = "s-(\D*)$"
}

# get all profiles that are now loaded that do not
# include the vendor and our new one
$allImageProfiles = Get-EsxImageProfile | ? {($_.Name -ne $baseprofile.Name) -and ($_.Name -ne $imgprofilename) -and ($_.Name -match $toolsFilter) -and ($_.Name -match $securityFilter)}

# cycle through the image profiles
# collect new packages and add to baseprofile
$allImageProfiles | % {
    $thisprofile = $_
    $delta = Compare-EsxImageProfile -ReferenceProfile $baseprofile.Name -ComparisonProfile $thisprofile.Name
    $deltaupdates = $delta | select -ExpandProperty UpgradeFromRef #upgrade vibs
    $deltaupdates += $delta | select -ExpandProperty OnlyInComp #new vibs
    if ($deltaupdates) {
        foreach ($d in $deltaupdates) {
            $pkg = Get-EsxSoftwarePackage | ? {$_.Guid -eq $d}
            Write-Verbose "Adding $pkg to $imgprofilename" -Verbose
            Add-EsxSoftwarePackage -ImageProfile $imgprofilename -SoftwarePackage $pkg
        }
    }
}
Set-EsxImageProfile -AcceptanceLevel CommunitySupported -ImageProfile $imgprofilename
#Export ISO + Bundle
Export-EsxImageProfile -ImageProfile $imgprofilename -ExportToBundle -FilePath $($exportpath + "/" + $imgprofilename + ".zip") -Force
if ($exportiso -eq $true) {
    Export-EsxImageProfile -ImageProfile $imgprofilename -ExportToISO -FilePath $($exportpath + "/" + $imgprofilename + ".iso") -Force
}
