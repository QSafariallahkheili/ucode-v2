import { describe, it, expect } from 'vitest'
import { HTTP } from "@/utils/http-common"

describe('HTTP Common utils test', () => {
  it('adds the default base url to the global axios object', () => {
    console.log(HTTP)
    expect(HTTP.defaults.baseURL).toBe("http://localhost:8000")
  })
})