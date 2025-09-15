// Example JavaScript client for OPC UA Delta Frames CSV Export

class OpcUaCsvExporter {
    constructor(baseUrl = '/api/publishing') {
        this.baseUrl = baseUrl;
    }

    /**
     * Export OPC UA delta frames as CSV with relative timestamps
     * @param {string} datasetId - The ID of the dataset to export
     * @param {Object} options - Export options
     * @param {boolean} options.useRelativeTimestamps - Use relative timestamps (default: true)
     * @param {Date} options.startTime - Filter data from this time
     * @param {Date} options.endTime - Filter data until this time
     * @param {Date} options.referenceTime - Reference time for relative timestamps
     * @param {string[]} options.tagFilter - Filter specific tag names
     * @returns {Promise<void>} - Downloads the CSV file
     */
    async exportDataset(datasetId, options = {}) {
        try {
            const params = new URLSearchParams();
            
            if (options.useRelativeTimestamps !== undefined) {
                params.append('useRelativeTimestamps', options.useRelativeTimestamps);
            }
            if (options.startTime) {
                params.append('startTime', options.startTime.toISOString());
            }
            if (options.endTime) {
                params.append('endTime', options.endTime.toISOString());
            }
            if (options.referenceTime) {
                params.append('referenceTime', options.referenceTime.toISOString());
            }
            if (options.tagFilter && options.tagFilter.length > 0) {
                options.tagFilter.forEach(tag => params.append('tagFilter', tag));
            }

            const url = `${this.baseUrl}/datasets/${datasetId}/export-csv?${params.toString()}`;
            
            // Fetch the CSV file
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`Export failed: ${response.statusText}`);
            }

            // Get filename from Content-Disposition header or generate one
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = 'opcua_deltaframes.csv';
            
            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
                if (filenameMatch && filenameMatch[1]) {
                    filename = filenameMatch[1].replace(/['"]/g, '');
                }
            }

            // Download the file
            const blob = await response.blob();
            this.downloadBlob(blob, filename);

            console.log(`Successfully exported OPC UA delta frames to ${filename}`);
        } catch (error) {
            console.error('Error exporting OPC UA delta frames:', error);
            throw error;
        }
    }

    /**
     * Export using POST method with JSON body (for complex requests)
     */
    async exportDatasetPost(datasetId, requestBody) {
        try {
            const url = `${this.baseUrl}/datasets/${datasetId}/export-csv`;
            
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });

            if (!response.ok) {
                throw new Error(`Export failed: ${response.statusText}`);
            }

            // Get filename from response header
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = 'opcua_deltaframes.csv';
            
            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
                if (filenameMatch && filenameMatch[1]) {
                    filename = filenameMatch[1].replace(/['"]/g, '');
                }
            }

            const blob = await response.blob();
            this.downloadBlob(blob, filename);

            console.log(`Successfully exported OPC UA delta frames to ${filename}`);
        } catch (error) {
            console.error('Error exporting OPC UA delta frames:', error);
            throw error;
        }
    }

    /**
     * Helper method to download blob as file
     */
    downloadBlob(blob, filename) {
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.style.display = 'none';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Clean up the URL object
        window.URL.revokeObjectURL(url);
    }

    /**
     * Get list of available datasets
     */
    async getDatasets() {
        try {
            const response = await fetch(`${this.baseUrl}/datasets`);
            
            if (!response.ok) {
                throw new Error(`Failed to get datasets: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error getting datasets:', error);
            throw error;
        }
    }
}

// Usage examples:

// Create exporter instance
const exporter = new OpcUaCsvExporter();

// Example 1: Simple export with relative timestamps
async function exportWithRelativeTimestamps() {
    await exporter.exportDataset('your-dataset-id', {
        useRelativeTimestamps: true
    });
}

// Example 2: Export specific tags for a time range
async function exportFilteredData() {
    const startTime = new Date('2024-01-01T10:00:00Z');
    const endTime = new Date('2024-01-01T14:00:00Z');
    
    await exporter.exportDataset('your-dataset-id', {
        useRelativeTimestamps: true,
        startTime: startTime,
        endTime: endTime,
        tagFilter: ['Temperature', 'Pressure']
    });
}

// Example 3: Export with custom reference time using POST
async function exportWithCustomReference() {
    const requestBody = {
        useRelativeTimestamps: true,
        referenceTime: '2024-01-01T12:00:00Z',
        tagFilter: ['Temperature', 'Pressure', 'Humidity']
    };
    
    await exporter.exportDatasetPost('your-dataset-id', requestBody);
}

// Example 4: Add export button to existing UI
function addExportButton(datasetId) {
    const button = document.createElement('button');
    button.textContent = 'Export OPC UA CSV';
    button.className = 'btn btn-primary';
    button.onclick = async () => {
        try {
            button.disabled = true;
            button.textContent = 'Exporting...';
            
            await exporter.exportDataset(datasetId, {
                useRelativeTimestamps: true
            });
            
            button.textContent = 'Export Complete!';
            setTimeout(() => {
                button.textContent = 'Export OPC UA CSV';
                button.disabled = false;
            }, 2000);
        } catch (error) {
            alert('Export failed: ' + error.message);
            button.textContent = 'Export OPC UA CSV';
            button.disabled = false;
        }
    };
    
    return button;
}

// Example 5: Export with progress indication
async function exportWithProgress(datasetId) {
    const progressDiv = document.createElement('div');
    progressDiv.innerHTML = '<div class="progress"><div class="progress-bar" style="width: 0%">Preparing export...</div></div>';
    document.body.appendChild(progressDiv);
    
    try {
        // Show progress
        const progressBar = progressDiv.querySelector('.progress-bar');
        progressBar.style.width = '50%';
        progressBar.textContent = 'Generating CSV...';
        
        await exporter.exportDataset(datasetId, {
            useRelativeTimestamps: true
        });
        
        progressBar.style.width = '100%';
        progressBar.textContent = 'Download complete!';
        
        setTimeout(() => {
            document.body.removeChild(progressDiv);
        }, 2000);
    } catch (error) {
        progressDiv.innerHTML = `<div class="alert alert-danger">Export failed: ${error.message}</div>`;
        setTimeout(() => {
            document.body.removeChild(progressDiv);
        }, 5000);
    }
}

// Export the class for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = OpcUaCsvExporter;
}