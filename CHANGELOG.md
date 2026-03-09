# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-24

### Added
- Initial public release
- **Matching Mode**: Direct microRNA-to-mRNA binding analysis
- **Dynamite Mode**: High-throughput miRNA database screening
- **BLAST Mode**: Sequence homology searching
- Support for FASTA and GenBank file formats
- NCBI GenBank integration for remote sequence retrieval
- Detailed Watson-Crick and wobble pairing analysis
- Threading support for non-blocking UI during long analyses
- Result export to file functionality
- Professional GUI with tabbed interface

### Fixed
- SSL certificate handling for NCBI queries

### Known Issues
- Large databases may require 5-10 seconds for analysis
- NCBI queries depend on internet connectivity

## Future Releases

### Planned for v1.1.0
- [ ] Command-line interface (CLI) mode
- [ ] Batch processing capabilities
- [ ] Additional file format support
- [ ] Result caching system
- [ ] Progress bars for long operations
- [ ] Unit tests and CI/CD pipeline

### Planned for v2.0.0
- [ ] REST API for integration with other tools
- [ ] Docker containerization
- [ ] Database of pre-computed results
- [ ] Advanced filtering and visualization options
- [ ] Performance optimizations
