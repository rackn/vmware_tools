<#
.SYNOPSIS
    Script to assist with building an ISO with the RackN Components.
.DESCRIPTION
    Script to build ISOs with drpy agent embeded.
.PARAMETER exportpath
    Full path to where you want the ISO exported. If it does not exist it will
    be created if it has permssion.
.PARAMETER imgprofilename
    Name for the new image profile. This script will add the prefix RKN to what ever name you provide here.
.PARAMETER offlineDepots
    A comma seperated list of full paths to the required offline bundles. At least 3 will be required. More are supported.
.EXAMPLE
    C:\PS> .\build_iso.ps1 -exportpath c:/temp/isos -imgprofilename Esxi-70-GA-RackN-Agent -depots c:/temp/depots/ESXi-7-depot.zip,c:/temp/depots/RKN-Agent.zip,c:/temp/depots/RKN-Firewall.zip
.NOTES
    Author: RackN
    Date: 06-2020
#>

param(
    [Parameter(Mandatory=$true, HelpMessage="Full Path to where you want the ISO exported")]
    [string]$exportpath,
    [Parameter(Mandatory=$true, HelpMessage="Name for the new image profile. This script will add the prefix RKN to what ever name you provide here.")]
    [string]$imgprofilename,
    [Parameter(Mandatory=$true)]
    [String[]]$offlineDepots
)
$imgprofilename = "RKN-$imgprofilename"

if ($offlineDepots.Count -lt 3) {
    echo "At least 3 depots must be set."
    echo "1. RackN Firewall"
    echo "2. RackN Agent"
    echo "3. ESXi Depot"
    echo "Additional are supported, but at least 3 will be needed for the build to work."
    echo "Ex: -depots c:/temp/RKN-DRPY-Agent.zip,c:/temp/RKN-FW-RULE.zip,c:/temp/ESXi-olb.zip"
    exit
}

## This should be edited
#$exportpath = "C:/Users/errr/projects/vmware_tools/grd"



#OPTIONS
$withtools = $false #use profile with VMtools or not
$exportiso = $true #export iso
$securityonly = $false #security only profiles

If(!(test-path $exportpath)) {
      New-Item -ItemType Directory -Force -Path $exportpath
}
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
New-EsxImageProfile -CloneProfile $baseprofile.Name -Name $imgprofilename -Vendor $baseprofile.vendor
#add in the DRPY Agent
Add-EsxSoftwarePackage -ImageProfile $imgprofilename -SoftwarePackage DRP-Firewall-Rule
Add-EsxSoftwarePackage -ImageProfile $imgprofilename -SoftwarePackage DRP-Agent

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
Set-EsxImageProfile -ImageProfile $imgprofilename
#Export ISO + Bundle
Export-EsxImageProfile -ImageProfile $imgprofilename -ExportToBundle -FilePath $($exportpath + "/" + $imgprofilename + ".zip")
if ($exportiso -eq $true) {
    Export-EsxImageProfile -ImageProfile $imgprofilename -ExportToISO -FilePath $($exportpath + "/" + $imgprofilename + ".iso")
}
