#! /project/home/sravishankar9/local/bin/python3.4
import os
import sys
import time
import logging
import datetime
import argparse
import subprocess
import configparser
from time import gmtime, strftime

logger = logging.getLogger('Nest - GATK')
logger.setLevel(logging.DEBUG)
stream = logging.StreamHandler()
stream.setLevel(logging.DEBUG)
formats = logging.Formatter('%(asctime)s;%(name)s;%(levelname)s;%(message)s')
stream.setFormatter(formats)
logger.addHandler(stream)

def target(samfile):
    logger.info('Running realigner target creator')
    interval = os.path.splitext(samfile)[0] + '.intervals'
    config = configparser.ConfigParser()
    config.read('config.cfg')
    java = config['General']['java']
    gatk = config['GATK']['gatk']
    maxint = config['GATK']['maxins']
    minreads = config['GATK']['minreads']
    mismatch = config['GATK']['mismatch']
    window = config['GATK']['window']
    threads = config['General']['threads']
    reference = config['General']['reference']
    exome = config['GATK']['exome']
   
    known = list()
    if config['GATK']['known'] == 'null':
        known = ['-known', config['General']['dbsnp']]
    else:
        for lines in config['GATK']['known'].split(','):
            known.append('-known')
            known.append(lines)

    
    trcr_args = [java, '-jar', gatk, '-T', 'RealignerTargetCreator', '-o',
        interval, '-maxInterval', maxint, '-minReads', minreads, '-mismatch',
        mismatch, '-window', window, '-nt', threads, '-I', samfile, '-R',
        reference ] + known
    if exome != 'null':
        trcr_args += ['-L', exome]
 
    try:
        run_trcr = subprocess.check_call(' '.join(trcr_args), shell=True)
        logger.info('Realginer target creator completed')
    except subprocess.CalledProcessError as ret:
        logger.info('GATK failed with return code: {0}'.format(ret.returncode))
        logger.info('GATK command: {0}'.format(ret.cmd))
        sys.exit()
    return(interval)


def realigner(samfile, interval):

    logger.info('Running indel realigner')
    bamfile = os.path.splitext(samfile)[0] + '_IR.bam'
    config = configparser.ConfigParser()
    config.read('config.cfg')
    java = config['General']['java']
    gatk = config['GATK']['gatk']
    model = config['GATK']['model']
    lod = config['GATK']['lod']
    entropy = config['GATK']['entropy']
    maxins = config['Bowtie']['maxins']
    maxmoves = config['GATK']['maxmoves']
    maxcon = config['GATK']['maxcon']
    reference = config['General']['reference']
    greedy = config['GATK']['greedy']
    maxreads = config['GATK']['maxreads']
    maxinmem = config['GATK']['maxinmem']
    exome = config['GATK']['exome']
    inre_args = [java, '-jar', gatk, '-T', 'IndelRealigner',
        '--targetIntervals', interval, '-o', bamfile, '-model', model, '-LOD',
        lod, '-entropy', entropy, '--maxConsensuses', maxcon, '-maxIsize',
        maxins, '-maxPosMove', maxmoves, '-greedy', greedy, '-maxReads',
        maxreads, '-maxInMemory', maxinmem, '-I', samfile, '-R', reference]
    if exome != 'null':
        inre_args += ['-L', exome]
 
    try:
        run_inre = subprocess.check_call(' '.join(inre_args), shell=True)
        logger.info('Indel realignment completed')
    except subprocess.CalledProcessError as ret:
        logger.info('GATK failed with return code: {0}'.format(ret.returncode))
        logger.info('GATK command: {0}'.format(ret.cmd))
        sys.exit()
    return(bamfile)

def baserecal(samfile):

    logger.info('Running base recalibrator')
    table = os.path.splitext(samfile)[0] + '.table'
    config = configparser.ConfigParser()
    config.read('config.cfg')
    java = config['General']['java']
    reference = config['General']['reference']
    gatk = config['GATK']['gatk']
    ics =  config['GATK']['ics']
    maxcyc = config['GATK']['maxcyc']
    mcs = config['GATK']['mcs']
    bqsrgpen = config['GATK']['bqsrpen']
    ddq = config['GATK']['ddq']
    idq = config['GATK']['idq']
    threads = config['General']['threads']
    exome = config['GATK']['exome']
    covariates = list()
    for covs in config['GATK']['covariates'].split(','):
        covariates.append('-cov')
        covariates.append(covs)
    knownsites = list()
    if config['GATK']['knownsites'] == 'None':
        knownsites = ['-knownSites',config['General']['dbsnp']]
    else:
        for sites in config['GATK']['knownsites'].split(','):
            knownsites.append('-knownSites')
            knownsites.append(sites)
    bsrc_args = [java, '-jar', gatk, '-T', 'BaseRecalibrator', '-R', reference,
        '-I', samfile, '-o', table, '-ics', ics, '-maxCycle', maxcyc, '-mcs', 
        mcs, '-bqsrBAQGOP', bqsrgpen, '-ddq', ddq, '-idq', idq, '-nct', 
        threads] + covariates + knownsites
    if exome != 'null':
        bsrc_args += ['-L', exome]
 
    try:
        run_bsrc = subprocess.check_call(' '.join(bsrc_args), shell=True)
        logger.info('Base recalibration completed')
    except subprocess.CalledProcessError as ret:
        logger.info('GATK failed with return code: {0}'.format(ret.returncode))
        logger.info('GATK command: {0}'.format(ret.cmd))
        sys.exit()
    return(table)

def printreads(samfile, table):

    logger.info('Running print reads')
    bamfile = os.path.splitext(samfile)[0] + '_BQ.bam'
    config = configparser.ConfigParser()
    config.read('config.cfg')
    java = config['General']['java']
    gatk = config['GATK']['gatk']
    reference = config['General']['reference']
    threads = config['General']['threads']
    exome = config['GATK']['exome']
    prre_args = [java, '-jar', gatk, '-T', 'PrintReads', '-R', reference, '-I',
            samfile, '-o', bamfile, '-BQSR', table, '-nct', threads]
    if exome != 'null':
        prre_args += ['-L', exome]
 
    try:
        run_prre = subprocess.check_call(' '.join(prre_args), shell=True)
        logger.info('Print reads completed')
    except subprocess.CalledProcessError as ret:
        logger.info('GATK failed with return code: {0}'.format(ret.returncode))
        logger.info('GATk command: {0}'.format(ret.cmd))
        sys.exit()
    return(bamfile)

def haplocaller(samfile):

    logger.info('Running haplotype caller')
    vcffile = os.path.splitext(samfile)[0] + '.g.vcf'
    config = configparser.ConfigParser()
    config.read('config.cfg')
    java = config['General']['java']
    gatk = config['GATK']['gatk']
    reference = config['General']['reference']
    dbsnp = config['General']['dbsnp']
    calconf = config['GATK']['calconf']
    emitconf = config['GATK']['emitconf']
    threads = config['General']['threads']
    gtmode = config['GATK']['gtmode']
    exome = config['GATK']['exome']
    erc = config['GATK']['erc']
    if erc == 'GVCF':
        vcffile = os.path.splitext(samfile)[0] + '.g.vcf'
    elif erc == 'NONE':
        vcffile = os.path.splitext(samfile)[0] + '.vcf'
    hpcl_args = [java, '-jar', gatk, '-T', 'HaplotypeCaller', '-R', reference,
        '-I', samfile, '--dbsnp', dbsnp, '-stand_call_conf', calconf, 
        '-stand_emit_conf', emitconf, '-o', vcffile, '-nct', threads, 
        '-gt_mode', gtmode, '-ERC', erc]
    if exome != 'null':
        hpcl_args += ['-L', exome]
    try:
        run_hpcl = subprocess.check_call(' '.join(hpcl_args), shell=True)
        logger.info('Haplotype caller completed')
    except subprocess.CalledProcessError as ret:
        logger.info('GATk failed with return code: {0}'.format(ret.returncode))
        logger.info('GATK command: {0}'.format(ret.cmd))
        sys.exit()
    return(vcffile)

def joint_genotyper(gvcf_list, outdir):

    logger.info('Running joint genotyping')
    vcffile = outdir + '/joint_calls.vcf'
    config = configparser.ConfigParser()
    config.read('config.cfg')
    java = config['General']['java']
    gatk = config['GATK']['gatk']
    reference = config['General']['reference']
    exome = config['GATK']['exome']
    variants = [' --variant '+ val for val in gvcf_list]
    jg_args = [java, '-jar', gatk, '-T', 'GenotypeGVCFs', '-R', reference, '-o',
        vcffile] + variants
    if exome != 'null':
        jg_args += ['-L', exome]
 
    try:
        run_jg = subprocess.check_call(' '.join(jg_args), shell=True)
        logger.info('Joint Genptyper completed')
    except subprocess.CalledProcessError as ret:
        logger.info('GATk failed with return code: {0}'.format(ret.returncode))
        logger.info('GATK command: {0}'.format(ret.cmd))
        sys.exit()
    return(vcffile)

def vqsr(vcf_file, outdir):
    logger.info('Running Variant recalibration')
    snprecalfile = outdir + '/joint_calls_SNP.recal'
    indelrecalfile = outdir + '/joint_calls_Indel.recal'
    snptranchesfile = outdir + '/joint_calls_SNP.tranches'
    indeltranchesfile = outdir + '/joint_calls_Indel.tranches'
    snprscript = outdir + '/joint_calls_SNP_plots.R'
    indelrscript = outdir + '/joint_calls_Indel_plots.R'
    config = configparser.ConfigParser()
    config.read('config.cfg')
    java = config['General']['java']
    gatk = config['GATK']['gatk']
    reference = config['General']['reference']
    known = config['GATK']['knownvqsr'].split(',')
    ann = config['GATK']['ann'].split(',')
    applymode = config['GATK']['applymode']
    exome = config['GATK']['exome']
    annotation = list()
    for lines in ann:
        annotation += ['-an', lines]
    mode = ['-mode', 'SNP', '-recalFile', snprecalfile, '-tranchesFile',
        snptranchesfile]
    vqsr_args = [java, '-jar', gatk, '-T', 'VariantRecalibrator', '-R', reference,
        '-input', vcf_file, '-rscriptFile', snprscript,
        '-resource:hapmap,known=false,training=true,truth=true,prior=15.0', known[0],
        '-resource:omni,known=false,training=true,truth=false,prior=12.0', known[1],
        '-resource:1000G,known=false,training=true,truth=false,prior=10.0', known[2],
        '-resource:dbsnp,known=true,training=false,truth=false,prior=6.0', known[3]]
    vqsr_args += annotation
    vqsrsnp_args = vqsr_args + mode
    mode = ['-mode', 'INDEL', '-recalFile', indelrecalfile, '-tranchesFile',
        indeltranchesfile]
    vqsrindel_args = vqsr_args + mode
    if exome != 'null':
        vqsrsnp_args += ['-L', exome]
        vqsrindel_args +=['-L', exome]
    try:
        if applymode == 'SNP':
            run_vqsr = subprocess.check_call(' '.join(vqsrsnp_args), shell=True)
            indelrecalfile = None
            indeltranchesfile = None
        elif applymode == 'INDEL':
            run_vqsr_indel = subprocess.check_call(' '.join(vqsrindel_args), shell=True)
            snprecalfile = None
            snptranchesfile = None 
        elif applymode == 'BOTH':
            run_vqsr = subprocess.check_call(' '.join(vqsrsnp_args), shell=True)
            run_vqsr_indel = subprocess.check_call(' '.join(vqsrindel_args), shell=True)
        logger.info('Variant quality score recalibration completed')
    except subprocess.CalledProcessError as ret:
        logger.info('GATK failed with return code: {0}'.format(ret.returncode))
        logger.info('GATK command: {0}'.format(ret.cmd))
        sys.exit()
    return(snprecalfile, indelrecalfile, snptranchesfile, indeltranchesfile)

def applyrecalibration(srf, irf, stf, itf, vcffile, outdir):
    logger.info('Running Apply recalibration')
    config = configparser.ConfigParser()
    config.read('config.cfg')
    java = config['General']['java']
    gatk = config['GATK']['gatk']
    reference = config['General']['reference']
    filterlevel = config['GATK']['filterlevel']
    applymode = config['GATK']['applymode']
    exome = config['GATK']['exome']
    outfile_snp = '{0}/joint_snp_call_filtered.vcf'.format(outdir)
    outfile_indel = '{0}/joint_indel_call_filtered.vcf'.format(outdir)
    if applymode == 'SNP':
        apply_args = [java, '-jar', gatk, '-T', 'ApplyRecalibration', '-R', reference,
            '-input', vcffile, '--ts_filter_level', filterlevel, '-tranchesFile', stf,
            '-recalFile', srf, '-mode', applymode, '-o', outfile_snp]
    elif applymode == 'INDEL':
        apply_args = [java, '-jar', gatk, '-T', 'ApplyRecalibration', '-R', reference,
            '-input', vcffile, '--ts_filter_level', filterlevel, '-tranchesFile', itf,
            '-recalFile', irf, '-mode', applymode, '-o', outfile_indel]
    elif applymode == 'BOTH':
        apply_snp_args = [java, '-jar', gatk, '-T', 'ApplyRecalibration', '-R', reference,
            '-input', vcffile, '--ts_filter_level', filterlevel, '-tranchesFile', stf,
            '-recalFile', srf, '-mode', 'SNP', '-o', outfile_snp]
        apply_indel_args = [java, '-jar', gatk, '-T', 'ApplyRecalibration', '-R', reference,
            '-input', vcffile, '--ts_filter_level', filterlevel, '-tranchesFile', itf, 
            '-recalFile', irf, '-mode', 'INDEL', '-o', outfile_indel] 
    if exome != 'null':
        apply_args += ['-L', exome]
 
    try:
        if applymode == 'SNP' or applymode == 'INDEL':
            run_apply = subporcess.check_call(' '.join(apply_args), shell=True)
        else:
            run_apply = subprocess.check_call(' '.join(apply_snp_args), shell=True)
            run_apply = subprocess.check_call(' '.join(apply_indel_args), shell=True)
        logger.info('Apply recalibration completed')
    except subprocess.CalledProcessError as ret:
        logger.info('GATK failed with return code: {0}'.format(ret.returncode))
        logger.info('GATK command: {0}'.format(ret.cmd))
        sys.exit()
    return(outfile_snp, outfile_indel)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run GATK')
    parser.add_argument('-b', type=str, dest='bamfile', help='Bam file path')
    parser.add_argument('-i', type=str, dest='interval', help='Interval file')
    parser.add_argument('-t', type=str, dest='table', help='BQSR table file')
    parser.add_argument('-v', type=str, dest='vcffile', help='Vcf file') 
    parser.add_argument('-o', type=str, dest='outdir', help='Output directory path')
    args = parser.parse_args()
    #interval = target(args.bamfile)
    #bam = realigner(args.bamfile, interval)
    #table = baserecal(args.bamfile)
    #bam = printreads(args.bamfile, table)
    #vcffile = haplocaller(args.bamfile, args.outdir)
    srf, irf, stf, itf = vqsr(args.vcffile, args.outdir)
    #vcffile = applyrecalibration(srf, irf, stf, itf, vcffile, outdir)
