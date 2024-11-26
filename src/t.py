import pandas as pd
import sys

def read_tsv(file):
    """
    Чтение TSV файла. Возвращает два DataFrame: один для данных, второй для шапки (метаинформации).
    """
    with open(file, 'r') as f:
        header_lines = []
        data_lines = []

        for line in f:
            if line.startswith('#'):
                header_lines.append(line.strip())
            else:
                data_lines.append(line.strip())
        
        # Преобразование шапки в DataFrame
        header_data = []
        for line in header_lines:
            # Убираем "Column description. " и "#", затем разделяем по "="
            line = line.replace("#", "").replace("Column description. ", "")
            if "=" in line:
                key, value = line.split("=", 1)
                header_data.append([key.strip(), value.strip()])
        
        header_df = pd.DataFrame(header_data, columns=["Тип данных", "Значение"])
        
        # Преобразование данных в DataFrame
        from io import StringIO
        data_str = '\n'.join(data_lines)
        data_df = pd.read_csv(StringIO(data_str), sep='\t')
        if 'uid' in data_df.columns:
            data_df = data_df.drop(columns=['uid'])

        # Переименование колонок
        rename_dict = {'chrom': 'Chrom', 'pos': 'Position', 'ref_base': 'Ref Base', 'alt_base': 'Alt Base', 'note_variant': 'Variant Note',
                       'coding': 'Coding', 'hugo': 'Gene', 'transcript': 'Transcript', 'so': 'Sequence Ontology', 'exonno': 'Exon Number',
                        'cchange': 'cDNA change', 'achange': 'Protein Change', 'all_mappings': 'All Mappings', 'gposend': 'End Position',
                        'numsample': 'Sample Count', 'samples': 'Samples', 'tags': 'Tags', 'hg19.chrom': 'hg19 Chrom', 'hg19.pos': 'hg19 Position',
                        'cardioboost.cardiomyopathy': 'CardioBoost Cardiomyopathy Score', 'cardioboost.cardiomyopathy1': 'CardioBoost Cardiomyopathy Class',
                        'cardioboost.arrhythmias': 'CardioBoost Arrhythmia Score', 'cardioboost.arrhythmias1': 'CardioBoost Arrhythmia Class',
                        'clinpred.score': 'ClinPred Score', 'clinpred.rankscore': 'ClinPred Rank Score', 'clinvar.sig': 'ClinVar Clinical Significance',
                        'clinvar.disease_refs': 'ClinVar Disease Ref Nums', 'clinvar.disease_refs_incl': 'ClinVar Disease Ref Nums Included Variant',
                        'clinvar.disease_names': 'ClinVar Disease Names', 'clinvar.clinvar_preferred_names': 'ClinVar Preferred Disease Names',
                        'clinvar.hgvs': 'ClinVar HGVS', 'clinvar.rev_stat': 'ClinVar Review Status', 'clinvar.id': 'ClinVar ClinVar ID',
                        'clinvar.sig_conf': 'ClinVar Significance Detail', 'clinvar.sig_conf_incl': 'ClinVar Significance Detail',
                        'clinvar.af_go_esp': 'ClinVar Allele Frequencies GO-ESP', 'clinvar.af_exac': 'ClinVar Allele Frequencies EXAC',
                        'clinvar.af_tgp': 'ClinVar Allele Frequencies TGP', 'clinvar.clinvar_allele_id': 'ClinVar Clinvar Allele Id',
                        'clinvar.variant_type': 'ClinVar Variant Type', 'clinvar.variant_type_sequence_ontology': 'ClinVar Variant Type SO',
                        'clinvar.variant_clinical_sources': 'ClinVar Variant Clinical Sources', 'clinvar.dbvar_id': 'ClinVar DBVAR ID',
                        'clinvar.clinvar_gene_info': 'ClinVar Gene names for the variant', 'clinvar.gene_info': 'ClinVar Molecular Consequence',
                        'clinvar.onc_disease_name': 'ClinVar Oncogenecity Disease Names', 'clinvar.onc_disease_name_incl': 'ClinVar Oncogenecity Disease Names Incl',
                        'clinvar.onc_disease_refs': 'ClinVar Oncogenecity Disease References',
                        'clinvar.onc_disease_refs_incl': 'ClinVar Oncogenecity Disease References Incl',
                        'clinvar.onc_classification': 'ClinVar Oncogenecity Classification',
                        'clinvar.onc_classification_type': 'ClinVar Oncogenecity Classification Type', 'clinvar.onc_rev_stat': 'ClinVar Oncogenecity Review Status',
                        'clinvar.onc_classification_conflicting': 'ClinVar Conflicting Oncogenecity Classification',
                        'clinvar.allele_origin': 'ClinVar Allele Origin', 'clinvar.dbsnp_id': 'ClinVar DBSNP ID',
                        'clinvar.somatic_disease_name': 'ClinVar Somatic Disease Name', 'clinvar.somatic_disease_name_incl': 'ClinVar Somatic Disease Name Incl',
                        'clinvar.somatic_refs': 'ClinVar Somatic References', 'clinvar.somatic_refs_incl': 'ClinVar Somatic References Incl',
                        'clinvar.somatic_rev_stat': 'ClinVar Somatic Review Status', 'clinvar.somatic_impact': 'ClinVar Somatic Impact',
                        'clinvar.somatic_impact_incl': 'ClinVar Somatic Impact Incl', 'clinvar.germline_or_somatic': 'ClinVar Germline or Somatic',
                        'clinvar_acmg.ps1_id': 'ClinVar ACMG PS1 ID', 'clinvar_acmg.pm5_id': 'ClinVar ACMG PM5 ID',
                        'extra_vcf_info.pos': 'Extra VCF INFO Annotations VCF Position', 'extra_vcf_info.ref': 'Extra VCF INFO Annotations VCF Ref Allele',
                        'extra_vcf_info.alt': 'Extra VCF INFO Annotations VCF Alt Allele', 'extra_vcf_info.NS': 'Extra VCF INFO Annotations NS',
                        'extra_vcf_info.DP': 'Extra VCF INFO Annotations DP', 'extra_vcf_info.DPB': 'Extra VCF INFO Annotations DPB',
                        'extra_vcf_info.AC': 'Extra VCF INFO Annotations AC', 'extra_vcf_info.AN': 'Extra VCF INFO Annotations AN',
                        'extra_vcf_info.AF': 'Extra VCF INFO Annotations AF', 'extra_vcf_info.RO': 'Extra VCF INFO Annotations RO',
                        'extra_vcf_info.AO': 'Extra VCF INFO Annotations AO', 'extra_vcf_info.PRO': 'Extra VCF INFO Annotations PRO',
                        'extra_vcf_info.PAO': 'Extra VCF INFO Annotations PAO', 'extra_vcf_info.QR': 'Extra VCF INFO Annotations QR',
                        'extra_vcf_info.QA': 'Extra VCF INFO Annotations QA', 'extra_vcf_info.PQR': 'Extra VCF INFO Annotations PQR',
                        'extra_vcf_info.PQA': 'Extra VCF INFO Annotations PQA', 'extra_vcf_info.SRF': 'Extra VCF INFO Annotations SRF',
                        'extra_vcf_info.SRR': 'Extra VCF INFO Annotations SRR', 'extra_vcf_info.SAF': 'Extra VCF INFO Annotations SAF',
                        'extra_vcf_info.SAR': 'Extra VCF INFO Annotations SAR', 'extra_vcf_info.SRP': 'Extra VCF INFO Annotations SRP',
                        'extra_vcf_info.SAP': 'Extra VCF INFO Annotations SAP', 'extra_vcf_info.AB': 'Extra VCF INFO Annotations AB',
                        'extra_vcf_info.ABP': 'Extra VCF INFO Annotations ABP', 'extra_vcf_info.RUN': 'Extra VCF INFO Annotations RUN',
                        'extra_vcf_info.RPP': 'Extra VCF INFO Annotations RPP', 'extra_vcf_info.RPPR': 'Extra VCF INFO Annotations RPPR',
                        'extra_vcf_info.RPL': 'Extra VCF INFO Annotations RPL', 'extra_vcf_info.RPR': 'Extra VCF INFO Annotations RPR',
                        'extra_vcf_info.EPP': 'Extra VCF INFO Annotations EPP', 'extra_vcf_info.EPPR': 'Extra VCF INFO Annotations EPPR',
                        'extra_vcf_info.DPRA': 'Extra VCF INFO Annotations DPRA', 'extra_vcf_info.ODDS': 'Extra VCF INFO Annotations ODDS',
                        'extra_vcf_info.GTI': 'Extra VCF INFO Annotations GTI', 'extra_vcf_info.TYPE': 'Extra VCF INFO Annotations TYPE',
                        'extra_vcf_info.CIGAR': 'Extra VCF INFO Annotations CIGAR', 'extra_vcf_info.NUMALT': 'Extra VCF INFO Annotations NUMALT',
                        'extra_vcf_info.MEANALT': 'Extra VCF INFO Annotations MEANALT', 'extra_vcf_info.LEN': 'Extra VCF INFO Annotations LEN',
                        'extra_vcf_info.MQM': 'Extra VCF INFO Annotations MQM', 'extra_vcf_info.MQMR': 'Extra VCF INFO Annotations MQMR',
                        'extra_vcf_info.PAIRED': 'Extra VCF INFO Annotations PAIRED', 'extra_vcf_info.PAIREDR': 'Extra VCF INFO Annotations PAIREDR',
                        'extra_vcf_info.MIN_DP': 'Extra VCF INFO Annotations MIN_DP', 'extra_vcf_info.END': 'Extra VCF INFO Annotations END',
                        'hpo.id': 'Human Phenotype Ontology HPO ID', 'hpo.term': 'Human Phenotype Ontology HPO Term',
                        'hpo.all': 'Human Phenotype Ontology All Annotations', 'ncbigene.ncbi_desc': 'NCBI Gene Description', 'ncbigene.entrez': 'NCBI Gene Entrez ID',
                        'omim.omim_id': 'OMIM Entry ID', 'original_input.chrom': 'Original Input Chrom', 'original_input.pos': 'Original Input Pos',
                        'original_input.ref_base': 'Original Input Reference allele', 'original_input.alt_base': 'Original Input Alternate allele',
                        'spliceai.ds_ag': 'SpliceAI Acceptor Gain Score', 'spliceai.ds_al': 'SpliceAI Acceptor Loss Score', 'spliceai.ds_dg': 'SpliceAI Donor Gain Score',
                        'spliceai.ds_dl': 'SpliceAI Donor Loss Score', 'spliceai.dp_ag': 'SpliceAI Acceptor Gain Position',
                        'spliceai.dp_al': 'SpliceAI Acceptor Loss Position', 'spliceai.dp_dg': 'SpliceAI Donor Gain Position',
                        'spliceai.dp_dl': 'SpliceAI Donor Loss Posiiton', 'vcfinfo.phred': 'VCF Info Phred', 'vcfinfo.filter': 'VCF Info VCF filter',
                        'vcfinfo.zygosity': 'VCF Info Zygosity', 'vcfinfo.alt_reads': 'VCF Info Alternate reads', 'vcfinfo.tot_reads': 'VCF Info Total reads',
                        'vcfinfo.af': 'VCF Info Variant AF', 'vcfinfo.hap_block': 'VCF Info Haplotype block ID', 'vcfinfo.hap_strand': 'VCF Info Haplotype strand ID',
                        'gnomad.af': 'gnomAD Global AF', 'gnomad.af_afr': 'gnomAD African AF', 'gnomad.af_amr': 'gnomAD American AF',
                        'gnomad.af_asj': 'gnomAD Ashkenazi Jewish AF', 'gnomad.af_eas': 'gnomAD East Asian AF', 'gnomad.af_fin': 'gnomAD Finnish AF',
                        'gnomad.af_nfe': 'gnomAD Non-Fin Eur AF', 'gnomad.af_oth': 'gnomAD Other AF', 'gnomad.af_sas': 'gnomAD South Asian AF',
                        'gnomad4.af': 'gnomAD4 Global AF', 'gnomad4.af_afr': 'gnomAD4 African AF', 'gnomad4.af_ami': 'gnomAD4 Amish AF',
                        'gnomad4.af_amr': 'gnomAD4 American AF', 'gnomad4.af_asj': 'gnomAD4 Ashkenazi Jewish AF', 'gnomad4.af_eas': 'gnomAD4 East Asian AF',
                        'gnomad4.af_fin': 'gnomAD4 Finnish AF', 'gnomad4.af_mid': 'gnomAD4 Mid-East AF', 'gnomad4.af_nfe': 'gnomAD4 Non-Fin Eur AF',
                        'gnomad4.af_sas': 'gnomAD4 South Asian AF'}  
        data_df.rename(columns=rename_dict, inplace=True)

    return data_df, header_df

tsv = sys.argv[1]
af = float(sys.argv[2])
gene_panel = pd.read_excel(sys.argv[3])['Gene'].to_list()
res = sys.argv[4]

data, header = read_tsv(tsv)

af_df = data[data['gnomAD Global AF'] <= af].reset_index(drop=True)
panel_df = af_df[af_df['Gene'].isin(gene_panel)].reset_index(drop=True)

outs = {data:res, af_df:res.replace('.tsv', '_clinical.tsv'), panel_df:res.replace('.tsv', '_panel.tsv')}

for df, file in outs.items():
    df.to_csv(file, sep='\t')