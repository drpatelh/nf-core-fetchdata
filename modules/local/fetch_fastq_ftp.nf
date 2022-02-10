
process FETCH_FASTQ_FTP {
    tag "$meta.id"
    label 'process_low'
    label 'error_retry'

    conda (params.enable_conda ? "conda-forge::sed=4.7" : null)
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://containers.biocontainers.pro/s3/SingImgsRepo/biocontainers/v1.2.0_cv1/biocontainers_v1.2.0_cv1.img' :
        'biocontainers/biocontainers:v1.2.0_cv1' }"

    input:
    tuple val(meta), val(fastq)
    val keep_fastq_name

    output:
    tuple val(meta), path("*fastq.gz"), emit: fastq
    tuple val(meta), path("*md5")     , emit: md5
    path "versions.yml"               , emit: versions

    script:
    def args = task.ext.args ?: ''
    def prefix = task.ext.prefix ?: "${meta.id}"
    if (meta.single_end) {
        File r1 = new File("${fastq[0]}");
        def r1_name = keep_fastq_name ? "${r1.getName()}" : "${prefix}.fastq.gz"
        """
        curl \\
            $args \\
            -L ${fastq[0]} \\
            -o $r1_name

        echo "${meta.md5_1}  ${r1_name}" > ${r1_name}.md5
        md5sum -c ${r1_name}.md5

        cat <<-END_VERSIONS > versions.yml
        "${task.process}":
            curl: \$(echo \$(curl --version | head -n 1 | sed 's/^curl //; s/ .*\$//'))
        END_VERSIONS
        """
    } else {
        File r1 = new File("${fastq[0]}");
        File r2 = new File("${fastq[1]}");
        def r1_name = keep_fastq_name ? "${r1.getName()}" : "${prefix}_1.fastq.gz"
        def r2_name = keep_fastq_name ? "${r2.getName()}" : "${prefix}_2.fastq.gz"
        """
        curl \\
            $args \\
            -L ${fastq[0]} \\
            -o $r1_name

        echo "${meta.md5_1}  ${r1_name}" > ${r1_name}.md5
        md5sum -c ${r1_name}.md5

        curl \\
            $args \\
            -L ${fastq[1]} \\
            -o $r2_name

        echo "${meta.md5_2}  ${r2_name}" > ${r2_name}.md5
        md5sum -c ${r2_name}.md5

        cat <<-END_VERSIONS > versions.yml
        "${task.process}":
            curl: \$(echo \$(curl --version | head -n 1 | sed 's/^curl //; s/ .*\$//'))
        END_VERSIONS
        """
    }
}
