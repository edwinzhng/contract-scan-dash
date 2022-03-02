import { useEffect, useState } from "react";
import styled from "styled-components";
import ReactDiffViewer from "react-diff-viewer";
import { useSearchParams } from "react-router-dom";
import axios from "axios";

const API_BASE_URL = "https://rocketpooldata.com/api/";
const BASE_CONTRACT_ENDPOINT = "base_contract_code/";
const CONTRACT_CODE_ENDPOINT = "contract_code/";

interface Code {
  [key: string]: string;
}

interface IContractCode {
  name: string;
  code: Code;
  compiler_version: string;
}

const DiffPage = () => {
  const [searchParams] = useSearchParams();
  const diffName = searchParams.get("diff_name");
  const diffAddress = searchParams.get("addr");

  const [diffNameContract, setDiffNameContract] = useState<IContractCode>();
  const [addrContract, setAddrContract] = useState<IContractCode>();
  const [loading, setLoading] = useState(true);
  const [errors, setErrors] = useState<any[]>([]);

  useEffect(() => {
    const errors: any[] = [];
    axios
      .get<IContractCode>(API_BASE_URL + BASE_CONTRACT_ENDPOINT + diffName)
      .then((res) => setDiffNameContract(res.data))
      .catch((reason) => errors.push(reason));
    axios
      .get<IContractCode>(API_BASE_URL + CONTRACT_CODE_ENDPOINT + diffAddress)
      .then((res) => setAddrContract(res.data))
      .catch((reason) => errors.push(reason));
    setErrors(errors);
    setLoading(false);
  }, [diffName, diffAddress]);

  const formatCode = (code?: string) => {
    if (!code) {
      return "";
    }
    return (
      code
        .replaceAll("\\n", "\n")
        .replaceAll('\\"', '"')
        // Remove all blank lines
        .replace(/[\r\n]{2,}/g, "\n")
    );
  };

  const getContractCode = (name: string, contract: IContractCode) => {
    return formatCode(contract.code[name]);
  };

  const getContractFiles = (contract?: IContractCode): string[] => {
    if (!contract) {
      return [];
    }
    return contract
      ? Object.keys(contract.code).filter((key) => key !== contract.name)
      : [];
  };

  const diffNameContractFiles = getContractFiles(diffNameContract);
  const addrContractFiles = getContractFiles(addrContract);

  const sharedFiles = [...diffNameContractFiles].filter((x) =>
    addrContractFiles.includes(x)
  );
  const diffNameUniqueFiles = [...diffNameContractFiles].filter(
    (x) => !sharedFiles.includes(x)
  );
  const addrUniqueFiles = [...addrContractFiles].filter(
    (x) => !sharedFiles.includes(x)
  );

  return (
    <DiffPageWrapper>
      {loading && "Loading..."}
      {!loading && errors.length > 0 && <>{errors}</>}
      {!loading && diffNameContract && addrContract && errors.length === 0 && (
        <>
          <Title>Contract Diff</Title>
          <SubTitle>
            {diffNameContract.name} (Compiler Version{" "}
            {diffNameContract.compiler_version}) and {addrContract.name}{" "}
            (Compiler Version {addrContract.compiler_version})
          </SubTitle>

          <DiffSection>
            <DiffTitle>Base Contract</DiffTitle>
            <DiffWrapper>
              <ReactDiffViewer
                useDarkTheme={false}
                disableWordDiff
                oldValue={getContractCode(
                  diffNameContract.name,
                  diffNameContract
                )}
                newValue={getContractCode(addrContract.name, addrContract)}
                splitView={true}
              />
            </DiffWrapper>
          </DiffSection>

          <SubTitle>Shared Interfaces/Libraries</SubTitle>
          {sharedFiles.map((name) => (
            <DiffSection key={name}>
              <DiffTitle>{name}</DiffTitle>
              <DiffWrapper>
                <ReactDiffViewer
                  useDarkTheme={false}
                  disableWordDiff
                  oldValue={getContractCode(name, diffNameContract)}
                  newValue={getContractCode(name, addrContract)}
                  splitView={true}
                />
              </DiffWrapper>
            </DiffSection>
          ))}

          {diffNameUniqueFiles.length > 0 && (
            <>
              <SubTitle>Files only found in {diffNameContract.name}</SubTitle>
              {diffNameUniqueFiles.map((name) => (
                <DiffSection key={name}>
                  <DiffTitle>{name}</DiffTitle>
                  <DiffWrapper>
                    <ReactDiffViewer
                      useDarkTheme={false}
                      oldValue={getContractCode(name, diffNameContract)}
                      newValue={getContractCode(name, diffNameContract)}
                      splitView={false}
                    />
                  </DiffWrapper>
                </DiffSection>
              ))}
            </>
          )}

          {addrUniqueFiles.length > 0 && (
            <>
              <SubTitle>Files only found in {addrContract.name}</SubTitle>
              {addrUniqueFiles.map((name) => (
                <DiffSection key={name}>
                  <DiffTitle>{name}</DiffTitle>
                  <DiffWrapper>
                    <ReactDiffViewer
                      useDarkTheme={false}
                      oldValue={getContractCode(name, addrContract)}
                      newValue={getContractCode(name, addrContract)}
                      splitView={false}
                    />
                  </DiffWrapper>
                </DiffSection>
              ))}
            </>
          )}
        </>
      )}
    </DiffPageWrapper>
  );
};

export default DiffPage;

/* Styles */
const DiffPageWrapper = styled.div`
  margin: 20px 32px;
`;

const DiffWrapper = styled.div`
  max-height: 600px;
  overflow-y: scroll;
  padding: 0 16px;
`;

const DiffSection = styled.div`
  margin-bottom: 40px;
`;

const Title = styled.div`
  text-align: center;
  color: #fff;
  font-size: 32px;
  font-weight: 600;
  width: 100%;
  margin: 20px auto;
`;

const SubTitle = styled.div`
  text-align: center;
  color: #a8a8a8;
  font-size: 24px;
  font-weight: 400;
  width: 100%;
  margin: 20px auto;
`;

const DiffTitle = styled.div`
  text-align: left;
  color: #f9fbfd;
  font-size: 18px;
  font-weight: 600;
  margin-left: 16px;
  margin-bottom: 20px;
`;
