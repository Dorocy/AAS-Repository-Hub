/*******************************************************************************
 * Copyright (C) 2023 the Eclipse BaSyx Authors
 *
 * Permission is hereby granted, free of charge, to any person obtaining
 * a copy of this software and associated documentation files (the
 * "Software"), to deal in the Software without restriction, including
 * without limitation the rights to use, copy, modify, merge, publish,
 * distribute, sublicense, and/or sell copies of the Software, and to
 * permit persons to whom the Software is furnished to do so, subject to
 * the following conditions:
 *
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
 * LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 * OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
 * WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 *
 * SPDX-License-Identifier: MIT
 ******************************************************************************/

package org.eclipse.digitaltwin.basyx.aasenvironment.http;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CountDownLatch;




import java.nio.charset.StandardCharsets;
import org.eclipse.digitaltwin.aas4j.v3.dataformat.aasx.AASXDeserializer;
import org.eclipse.digitaltwin.aas4j.v3.dataformat.json.JsonDeserializer;
import org.eclipse.digitaltwin.aas4j.v3.dataformat.xml.XmlDeserializer;
import org.eclipse.digitaltwin.aas4j.v3.dataformat.xml.XmlSerializer;
import org.apache.poi.openxml4j.exceptions.InvalidFormatException;
import org.eclipse.digitaltwin.aas4j.v3.dataformat.core.DeserializationException;
import org.eclipse.digitaltwin.aas4j.v3.dataformat.core.SerializationException;
import org.eclipse.digitaltwin.basyx.aasenvironment.AasEnvironment;
import org.eclipse.digitaltwin.basyx.aasenvironment.base.DefaultAASEnvironment;
import org.eclipse.digitaltwin.basyx.aasenvironment.environmentloader.CompleteEnvironment;
import org.eclipse.digitaltwin.basyx.aasenvironment.environmentloader.CompleteEnvironment.EnvironmentType;
import org.eclipse.digitaltwin.basyx.core.exceptions.ElementDoesNotExistException;
import org.eclipse.digitaltwin.basyx.http.Base64UrlEncodedIdentifier;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.enums.ParameterIn;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;

import org.eclipse.digitaltwin.aas4j.v3.model.Environment;
import org.eclipse.digitaltwin.aas4j.v3.dataformat.json.JsonSerializer;

//import org.springframework.web.bind.annotation.RequestPart;
//import org.springframework.web.multipart.MultipartFile;
import org.eclipse.digitaltwin.aas4j.v3.dataformat.aasx.InMemoryFile;

import org.eclipse.digitaltwin.aas4j.v3.model.Submodel;
import org.eclipse.digitaltwin.aas4j.v3.model.SubmodelElement;
import org.eclipse.digitaltwin.aas4j.v3.model.SubmodelElementCollection;
import org.eclipse.digitaltwin.aas4j.v3.model.SubmodelElementList;




@jakarta.annotation.Generated(value = "io.swagger.codegen.v3.generators.java.SpringCodegen", date = "2023-05-08T12:36:05.278579031Z[GMT]")
@RestController
public class AasEnvironmentApiHTTPController implements AASEnvironmentHTTPApi {

	
	private static final String ACCEPT_JSON = "application/json";
	private static final String ACCEPT_XML = "application/xml";
	private static final String ACCEPT_AASX = "application/asset-administration-shell-package+xml";

	private final HttpServletRequest request;

	private final AasEnvironment aasEnvironment;

	@Autowired
	public AasEnvironmentApiHTTPController(HttpServletRequest request, AasEnvironment aasEnvironment) {
		this.request = request;
		this.aasEnvironment = aasEnvironment;
	}

	@Override
	public ResponseEntity<Resource> generateSerializationByIds(
			@Parameter(in = ParameterIn.QUERY, description = "The Asset Administration Shells' unique ids (UTF8-BASE64-URL-encoded)", schema = @Schema()) @Valid @RequestParam(value = "aasIds", required = false) List<String> aasIds,
			@Parameter(in = ParameterIn.QUERY, description = "The Submodels' unique ids (UTF8-BASE64-URL-encoded)", schema = @Schema()) @Valid @RequestParam(value = "submodelIds", required = false) List<String> submodelIds,
			@Parameter(in = ParameterIn.QUERY, description = "Include Concept Descriptions?", schema = @Schema(defaultValue = "true")) @Valid @RequestParam(value = "includeConceptDescriptions", required = false, defaultValue = "true") Boolean includeConceptDescriptions) {
		String accept = request.getHeader("Accept");

		if (!areParametersValid(accept, aasIds, submodelIds)) {
			return new ResponseEntity<Resource>(HttpStatus.BAD_REQUEST);
		}

		try {
			if (accept.equals(ACCEPT_AASX)) {
				byte[] serialization = aasEnvironment.createAASXAASEnvironmentSerialization(getOriginalIds(aasIds), getOriginalIds(submodelIds), includeConceptDescriptions);
				return new ResponseEntity<Resource>(new ByteArrayResource(serialization), HttpStatus.OK);
			}

			if (accept.equals(ACCEPT_XML)) {
				String serialization = aasEnvironment.createXMLAASEnvironmentSerialization(getOriginalIds(aasIds), getOriginalIds(submodelIds), includeConceptDescriptions);
				return new ResponseEntity<Resource>(new ByteArrayResource(serialization.getBytes()), HttpStatus.OK);
			}

			String serialization = aasEnvironment.createJSONAASEnvironmentSerialization(getOriginalIds(aasIds), getOriginalIds(submodelIds), includeConceptDescriptions);
			return new ResponseEntity<Resource>(new ByteArrayResource(serialization.getBytes()), HttpStatus.OK);
		} catch (ElementDoesNotExistException e) {
			return new ResponseEntity<Resource>(HttpStatus.NOT_FOUND);
		} catch (SerializationException | IOException e) {
			return new ResponseEntity<Resource>(HttpStatus.INTERNAL_SERVER_ERROR);
		}
	}

	@Override
	public ResponseEntity<Boolean> uploadEnvironment(
			@RequestParam(value = "file") MultipartFile envFile,
			@RequestParam(value = "ignore-duplicates", required = false, defaultValue = "false") boolean ignoreDuplicates) {
		try {
			EnvironmentType envType = EnvironmentType.getFromMimeType(envFile.getContentType());

			if (envType == null)
				envType = EnvironmentType.AASX;

			aasEnvironment.loadEnvironment(CompleteEnvironment.fromInputStream(envFile.getInputStream(), envType),
					ignoreDuplicates);

		} catch (InvalidFormatException e) {
			return new ResponseEntity<>(false, HttpStatus.BAD_REQUEST);
		} catch (DeserializationException | IOException e) {
			return new ResponseEntity<>(false, HttpStatus.INTERNAL_SERVER_ERROR);
		}
		return new ResponseEntity<>(true, HttpStatus.OK);
	}

	private List<String> getOriginalIds(List<String> ids) {
		List<String> results = new ArrayList<>();

		if (!areValidIds(ids))
			return results;

		ids.forEach(id -> {
			results.add(Base64UrlEncodedIdentifier.fromEncodedValue(id).getIdentifier());
		});

		return results;
	}

	private boolean areParametersValid(String accept, @Valid List<String> aasIds, @Valid List<String> submodelIds) {
		if (!areValidIds(aasIds) && !areValidIds(submodelIds))
			return false;

		return (accept.equals(ACCEPT_AASX) || accept.equals(ACCEPT_JSON) || accept.equals(ACCEPT_XML));
	}

	private boolean areValidIds(List<String> identifiers) {
		return identifiers != null && !identifiers.isEmpty();
	}
	
	@Override
	public ResponseEntity<Boolean> validateEnvironment(MultipartFile envFile) {
	    try {
	        EnvironmentType envType = EnvironmentType.getFromMimeType(envFile.getContentType());
	        if (envType == null)
	            envType = EnvironmentType.AASX;

	        CompleteEnvironment.fromInputStream(envFile.getInputStream(), envType);
	        return ResponseEntity.ok(true);

	    } catch (InvalidFormatException e) {
	        return ResponseEntity.badRequest().body(false);
	    } catch (DeserializationException | IOException e) {
	        return ResponseEntity.status(500).body(false);
	    }
	}
	
	@Override
	public ResponseEntity<String> parseAASXFile(@RequestParam("file") MultipartFile file) {
	    try {
	        EnvironmentType envType = EnvironmentType.getFromMimeType(file.getContentType());
	        if (envType == null)
	            envType = EnvironmentType.AASX;

	        CompleteEnvironment completeEnv = CompleteEnvironment.fromInputStream(file.getInputStream(), envType);
	        Environment environment = completeEnv.getEnvironment();

	        JsonSerializer jsonSerializer = new JsonSerializer();
	        String json = jsonSerializer.write(environment);

	        return ResponseEntity.ok(json);

	    } catch (InvalidFormatException e) {
	        return ResponseEntity.badRequest().body("Invalid format: " + e.getMessage());
	    } catch (DeserializationException | SerializationException | IOException e) {
	        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Error: " + e.getMessage());
	    }
	}

	@Override
	public ResponseEntity<Resource> downloadAASXFile(
	        @RequestParam("file") MultipartFile jsonFile,
	        @RequestParam(value = "format", defaultValue = "json") String format,
	        @RequestParam(value = "attachments", required = false) String attachmentsJson) {
	    try {
	        // 1. JSON → Environment 역직렬화
	        String jsonContent = new String(jsonFile.getBytes(), StandardCharsets.UTF_8);
	        JsonDeserializer deserializer = new JsonDeserializer();
	        Environment environment = deserializer.read(jsonContent, Environment.class);
	        
	        // 1-1. Environment 내의 File 요소들을 해싱 방식에 맞게 업데이트
//	        updateEnvironmentFilePaths(environment);

	        // 2. 첨부파일 파싱 (해싱 처리 포함 - 안하는걸로 바꿈 필요하면 수정)
	        List<InMemoryFile> relatedFiles = aasEnvironment.parseBase64Attachments(attachmentsJson);

	        // 3. 포맷별 직렬화 처리
	        byte[] resultBytes;
	        String contentType;
	        switch (format.toLowerCase()) {
	            case "xml":
	                contentType = "application/xml";
	                XmlSerializer xmlSerializer = new XmlSerializer();
	                resultBytes = xmlSerializer.write(environment).getBytes(StandardCharsets.UTF_8);
	                break;
	            case "aasx":
	                contentType = "application/asset-administration-shell-package+xml";
	                resultBytes = aasEnvironment.createAASXPackage(environment, relatedFiles);
	                break;
	            default:
	                contentType = "application/json";
	                JsonSerializer jsonSerializer = new JsonSerializer();
	                resultBytes = jsonSerializer.write(environment).getBytes(StandardCharsets.UTF_8);
	                break;
	        }
	        return ResponseEntity.ok()
	            .header("Content-Disposition", "attachment; filename=environment." + format)
	            .header("Content-Type", contentType)
	            .body(new ByteArrayResource(resultBytes));
	    } catch (Exception e) {
	        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
	                .body(new ByteArrayResource(("AASX 생성 실패: " + e.getMessage()).getBytes(StandardCharsets.UTF_8)));
	    }
	}

	// downloadAASXFile 메서드 내에서 Environment 객체를 생성한 직후에 호출
	private void updateEnvironmentFilePaths(Environment env) {
	    if (env.getSubmodels() != null) {
	        for (Submodel submodel : env.getSubmodels()) {
	            updateSubmodelFilePaths(submodel);
	        }
	    }
	}

	private void updateSubmodelFilePaths(Submodel submodel) {
	    if (submodel.getSubmodelElements() != null) {
	        for (SubmodelElement element : submodel.getSubmodelElements()) {
	            updateFileElementRecursive(element);
	        }
	    }
	}

	private void updateFileElementRecursive(SubmodelElement element) {
	    if (element instanceof org.eclipse.digitaltwin.aas4j.v3.model.File) {
	        org.eclipse.digitaltwin.aas4j.v3.model.File fileElement = (org.eclipse.digitaltwin.aas4j.v3.model.File) element;
	        String origPath = fileElement.getValue(); // 원본 파일 경로
	        // DefaultAASEnvironment.getFilePathInAASX() 해싱된 경로를 생성. 해싱을 하든 안하든 맞춰야 됨
	        String newPath = DefaultAASEnvironment.getFilePathInAASX(origPath);
	        fileElement.setValue(newPath);
	    } else if (element instanceof SubmodelElementCollection) {
	        for (SubmodelElement child : ((SubmodelElementCollection) element).getValue()) {
	            updateFileElementRecursive(child);
	        }
	    } else if (element instanceof SubmodelElementList) {
	        for (SubmodelElement child : ((SubmodelElementList) element).getValue()) {
	            updateFileElementRecursive(child);
	        }
	    }
	}


	
}
